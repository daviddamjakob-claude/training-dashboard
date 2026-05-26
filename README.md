# Training Dashboard

A personal training dashboard that pulls live data from Strava and displays it as a static single-page app on GitHub Pages.

**Live URL:** https://daviddamjakob-claude.github.io/training-dashboard

## Features

- 5 views: Overview, By Week, By Month, All Activities, Hyrox Races
- OAuth login via Strava (tokens stored in localStorage, auto-refreshed)
- Activities cached for 30 minutes; re-fetched on next load
- Charts: sessions by type, volume by type, Hyrox progression & station comparisons
- Deep dive on any activity row
- Installable as iPhone home screen app (PWA)

## Setup (one-time)

1. Go to [strava.com/settings/api](https://www.strava.com/settings/api) and create an app:
   - Website: `https://daviddamjakob-claude.github.io/training-dashboard`
   - Authorization Callback Domain: `daviddamjakob-claude.github.io`

2. Open the live URL in your browser and click **Connect with Strava**.

3. Authorize the app — you'll be redirected back and data will load automatically.

## iPhone home screen

Open the live URL in Safari → tap the Share icon → **Add to Home Screen**.

## Re-authentication

If the session expires (rare — tokens refresh automatically), just click Connect with Strava again.
