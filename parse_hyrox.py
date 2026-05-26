#!/usr/bin/env python3
"""
Parse a Hyrox results detail URL and print the JS race object for index.html.

Usage:
  python parse_hyrox.py "<hyrox-results-url>"

The URL should be the detail page for a single athlete, e.g.:
  https://results.hyrox.com/season-8/?content=detail&fpid=list&pid=list&idp=...
"""

import sys
import re

STATION_NAME_MAP = {
    "skierg": "SkiErg",
    "sled push": "Sled Push",
    "sled pull": "Sled Pull",
    "burpee broad jump": "Burpee BJ",
    "row": "Row",
    "farmers carry": "Farmers Carry",
    "sandbag lunges": "Sandbag Lunges",
    "wall balls": "Wall Balls",
}

def shorten_station(name):
    low = name.lower()
    for key, short in STATION_NAME_MAP.items():
        if key in low:
            return short
    # fallback: strip leading distance (e.g., "1000m ")
    name = re.sub(r'^\d+m\s*', '', name)
    return name

def fmt_time(hms):
    """Convert HH:MM:SS to M:SS or MM:SS or H:MM:SS, stripping leading zeros."""
    parts = hms.strip().split(":")
    if len(parts) == 3:
        h, m, s = parts
        if int(h) > 0:
            return f"{int(h)}:{m}:{s}"
        return f"{int(m)}:{s}"
    return hms

def time_to_secs(hms):
    parts = hms.strip().split(":")
    parts = [int(p) for p in parts]
    if len(parts) == 3:
        return parts[0]*3600 + parts[1]*60 + parts[2]
    if len(parts) == 2:
        return parts[0]*60 + parts[1]
    return parts[0]

def fetch_page(url):
    import subprocess
    result = subprocess.run(
        ["curl", "-s", "-L", "-A",
         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
         url],
        capture_output=True
    )
    return result.stdout.decode("utf-8", errors="replace")

def extract_field(html, field_class):
    """Extract text from first <td class="...field_class...">content<."""
    pat = r'<td class="[^"]*' + re.escape(field_class) + r'[^"]*">([^<]+)<'
    m = re.search(pat, html)
    return m.group(1).strip() if m else None

def parse(url):
    html = fetch_page(url)

    # --- Scalar fields ---
    meeting = extract_field(html, "f-__meeting") or "Unknown Race"
    finish  = extract_field(html, "f-time_finish_netto") or "00:00:00"
    rank_all = extract_field(html, "f-place_all") or "?"
    rank_ag  = extract_field(html, "f-place_age") or "?"

    # Sex from URL (default M/W)
    sex_m = re.search(r'search(?:%5B|\[)sex(?:%5D|\])=([^&]+)', url)
    sex_label = "M/W" if not sex_m or sex_m.group(1).upper().startswith("M") else "W/W"

    # Race name: strip year prefix (e.g., "2026 Barcelona" → "Barcelona")
    race_name = re.sub(r'^\d{4}\s*', '', meeting).strip()
    # Optionally append division (e.g., "Saturday" or "Friday") if not standard
    division = extract_field(html, "f-__event") or ""

    # --- Parse workout summary table ---
    # Each row: <tr class="... f-time_XX ..."><th>Label</th><td>Time</td><td>Rank</td></tr>
    row_pat = re.compile(
        r'<tr class="([^"]*)">\s*<th[^>]*>([^<]+)</th>\s*<td[^>]*>([^<]+)</td>\s*<td[^>]*>(.*?)</td>',
        re.DOTALL
    )

    runs = []
    stations = []
    run_total = run_rank = roxzone = rox_rank = None

    for m in row_pat.finditer(html):
        cls, label, time_val, rank_td = m.groups()
        label = label.strip()
        time_val = time_val.strip()
        # Extract rank from rank_td (may contain <span> for dash)
        rank_val = re.sub(r'<[^>]+>', '', rank_td).strip()
        rank_val = None if rank_val in ('–', '&ndash;', '') else rank_val

        if "f-time_0" in cls and re.search(r'f-time_0[1-8]\b', cls):
            runs.append(fmt_time(time_val))
        elif re.search(r'f-time_1[1-8]\b', cls):
            stations.append({
                "name": shorten_station(label),
                "time": fmt_time(time_val),
                "rank": f"#{rank_val}" if rank_val else "—",
            })
        elif "f-time_49" in cls:
            run_total = fmt_time(time_val)
            run_rank = f"#{rank_val}" if rank_val else "—"
        elif "f-time_60" in cls:
            roxzone = fmt_time(time_val)
            rox_rank = f"#{rank_val}" if rank_val else "—"

    finish_fmt = fmt_time(finish)
    finish_secs = time_to_secs(finish)

    # --- Output JS object ---
    station_js = ",\n      ".join(
        "{name:'%s',time:'%s',rank:'%s'}" % (s["name"], s["time"], s["rank"])
        for s in stations
    )
    runs_js = ",".join(f"'{r}'" for r in runs)

    print(f"""  {{
    name:'{race_name}',
    date:'TODO fill in date',
    time:'{finish_fmt}',
    timeSecs:{finish_secs},
    rank:'#{rank_all} {sex_label}',
    ag:'#{rank_ag}',
    pb:false,
    target:false,
    runTotal:'{run_total}',
    runRank:'{run_rank}',
    roxzone:'{roxzone}',
    rxRank:'{rox_rank}',
    stations:[
      {station_js}
    ],
    runs:[{runs_js}]}},""")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    parse(sys.argv[1])
