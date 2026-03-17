# ⬡ Strava Viewer 3.0

Desktop application to analyze, visualize, and compare running activities downloaded from Strava. Native GUI (tkinter), light/dark theme and MongoDB as the sole storage backend.

---

> If this project is useful to you and you'd like to buy the developer a virtual coffee, you can do it here → [☕ PayPal](https://paypal.me/TeoVr81). No pressure — every km counts, donation or not.

---

## Features

### Opening activities
- Download all your runs directly from Strava with the **Download from Strava** button — activities are saved to MongoDB

### Dashboard
Complete overview of the open activity:
- Distance, active/total time, average and best pace, speed
- Positive and negative elevation gain
- Average and maximum heart rate, cadence, calories
- Performance indices (Suffer Score, VAM, etc.)

### Charts
Five charts embedded in the interface:
- **Pace per km** — colored bars (green = faster than average, blue = average, red = slower)
- **Speed** — line with filled area
- **Elevation** — bar chart
- **Heart rate** — time series line
- **Cadence** — trend per kilometer

### HR Zones
- Manual setting of maximum heart rate
- Time distribution per zone (Z1–Z5) with colored horizontal bars
- HR vs pace scatter plot with trend line and zone bands

### GPS Map
The map opens in the **default browser** (Chrome, Edge, Firefox…) and includes:

- **Layer switcher** — four selectable backgrounds from the top-right panel:
  - *Dark* (CartoDB dark matter, default)
  - *OpenStreetMap*
  - *Satellite* (Esri WorldImagery, real satellite imagery, no API key required)
  - *Light* (CartoDB positron)
- **Pace-colored track** — the polyline is split km by km with a green → yellow → red gradient (green = fastest km, red = slowest km); hovering over each segment shows a tooltip with pace, HR and elevation of that km
- **Kilometer markers** — a numbered indicator for each completed km; clicking opens a popup with pace, average HR and elevation for that kilometer
- **Enhanced Start/End popups** — green (start) and red (end) markers with full popups: date, distance, time, average/best pace, HR, elevation, calories, Suffer Score
- **Statistics overlay** — fixed bar at the top of the map with key activity metrics (name, distance, time, pace, HR, elevation)
- **FullScreen button** — expands the map to full screen in the browser
- **MiniMap** — 150×150 overview map in the bottom-right corner for orientation during zoom; toggleable

Requires Strava permission `activity:read_all` for the GPS polyline and an internet connection to load tiles in the browser.

### Splits
Scrollable table with kilometer-by-kilometer data:
- Distance, time, pace, speed, HR, elevation, cadence
- Pace color to immediately identify the fastest/slowest km

### Interval Detection *(new)*
Automatic detection and analysis of structured interval workouts directly from per-km splits:
- **Automatic detection** — the algorithm computes pace mean and standard deviation and labels each km as *fast*, *slow* or *neutral* using a ±0.5σ threshold; requires at least 3 fast segments and a coefficient of variation ≥ 6% to classify the session as intervals
- **Workout classification** — automatically identifies session type: *VO₂max Intervals*, *Threshold Intervals*, *Tempo / Progressive*, *Fartlek*, *Easy Strides*
- **Analytics strip** — 4 stat cards: average work pace, average recovery pace, fade rate (last vs first interval), consistency score (0–100)
- **Segment table** — scrollable list of all detected segments with type (⚡ Work / ○ Rest), distance, time, pace, HR and delta vs average; work intervals highlighted with orange left border
- **Charts** — pace bar chart per segment (orange = work, blue = rest) with reference lines for work/recovery averages; HR line chart per segment when heart rate data is available
- For non-interval sessions, shows a clear "Not an interval session" message with pace uniformity statistics

### Best Efforts
List of best efforts detected by Strava (1 km, 5 km, 10 km, half marathon, marathon, etc.) with 🏆 badge for personal records.

### Compare
Side-by-side comparison of up to 5 activities:
- Comparative table with green (best) and red (worst) highlighting for each metric
- Overlaid km-by-km pace chart
- Overlaid heart rate chart
- Add activities from the Library tab with the ➕ button

### Library
List of all runs saved in the database, with:
- **Pagination** — 100 rows per page with ◀ ▶ navigation
- **Filters** by name/description, distance (min–max km), date range, and **Races only** (filters activities with `workout_type = race`)
- **Semantic** pace color: green < 5:00/km, yellow < 6:30/km, red above
- Row hover with visual highlighting
- Open activity with 📂, add to comparison with ➕, delete with 🗑
- MongoDB connection status indicator

### Calendar
Monthly view of all runs with month-by-month navigation:
- Each cell with a run shows distance, pace and heart rate; the orange color intensity is **proportional to the km covered** compared to the longest day of the month (heatmap)
- Days with multiple runs show an additional counter with ◀ ▶ buttons to scroll through runs on the same day
- ◀ ▶ buttons to navigate between months, "Today" to return to the current month
- Clicking a cell opens the activity in the Dashboard tab
- The total km and number of runs for the month is displayed in the header

### Statistics
Aggregate statistics on **all** runs in the database (ignores filters and pagination):
- **Annual goal** — set a km target for the current year with progress bar; the value is saved in MongoDB and remembered between sessions
- Totals: runs, km, hours, elevation, average pace, average HR, calories, km/week
- **Activity heatmap** — GitHub-style calendar grid of the last 52 weeks (rows = days of the week Mon→Sun, columns = weeks): each cell is colored in orange with intensity proportional to km run that day, dark gray if resting; color scale bar below; mouse hover tooltip with date and km
- **Athletic profile** — hexagonal radar chart with 6 normalized 0–100 dimensions: *Speed* (average pace, scale 8:20→3:20/km), *Endurance* (median distances, scale 3→42 km), *Elevation* (average m↑/km, scale 0→40 m/km), *Consistency* (% weeks with at least one run in the last 52), *Volume* (average km/week in the last 52, scale 0→70), *Progression* (comparison of average pace last 3 months vs previous 3 months); alongside a panel with numeric scores, proportional bars and description of each dimension
- **Monthly table** — last 12 months with km, runs, time, average pace, elevation; bar chart of km per month
- Annual table with km, runs, time, average pace, elevation; km per year and runs per year chart
- Distance distribution (pie chart)
- **Training load** — ATL/CTL/TSB chart (Banister TRIMP) of the last 12 months:
  - *CTL (Fitness)* — 42-day exponential weighted average
  - *ATL (Fatigue)* — 7-day exponential weighted average
  - *TSB (Form)* — CTL − ATL (positive = rested, negative = fatigued)
- **Personal records** — table with the best personal time for canonical distances (1 km, 5 km, 10 km, Half Marathon, Marathon), with activity name and date achieved
- **Grade Analysis** — bar chart of median pace split by 6 gradient bands (from steep downhill <−8% to uphill >8%), calculated from 1 km splits recorded by Strava; "Last days" and "Races only" filters; data from this chart feeds the custom elevation correction for Performance Prediction; ℹ button with guide per band and training suggestions
- **Performance curve** — log-log plot of distance vs time on best efforts (from 400m to marathon) with power law fit `t = A × d^b`; times used are `moving_time` (pauses excluded); "Last days" and "Races only" filters; the exponent `b` reveals athletic profile (sprinter vs endurance runner, comparison with Riegel's b=1.06); ℹ button with theory and interpretive guide
- **Performance prediction (Monte Carlo)** — estimate of time over any distance with simulation of 5000 scenarios; configurable parameters: target distance (standard or custom in km), positive elevation of the route, historical time window (last N days), minimum and maximum length of runs from which to retrieve best efforts (min/max km), races only filter; elevation correction is customized: calculated via linear regression on your real splits (sec/km per 1% gradient), with fallback to Minetti model if data is insufficient; the result is a histogram with P10/P25/P50/P75/P90 percentiles and a diagnostic panel with data used in the fit, the b coefficient and the raw base time; ℹ button with complete guide on parameters, calculation and interpretation of results
- **Race analysis and VDOT** — analyzes all activities classified as "Race" on Strava (`workout_type = 1`) and calculates for each the VDOT according to Jack Daniels' formula (aerobic capacity index derived from actual distance and time, without lab testing); shows three stat cards (total races, best VDOT, most recent VDOT), a line chart of VDOT evolution over time with dashed line at historical maximum, a paginated race table (10 per page, clickable to open the activity) with date, km, time, VDOT and name, and a prediction table for 1K / 5K / 10K / half marathon / marathon calculated from the VDOT of the last recorded race; ℹ button with formula explanation, reference value table (beginner → elite) and guide to interpreting predictions
- **Recurring routes** — automatically detects routes you have run at least 3 times by grouping activities by starting area (~300 m) and distance (±1 km); for each group shows: scrollable list with most frequent name, distance, number of runs, period and city/coordinates; scatter chart of pace over time with green→red coloring (faster→slower), dashed trend line, highlighting of the best run and the latest; header with best pace, average pace and trend indicator (improved/worsened/stable); list of group runs with date, km, pace, HR and name, clickable to open the activity; city is retrieved first from Strava metadata, then via Nominatim reverse geocoding (OpenStreetMap) with persistent cache on MongoDB, sequential thread with 1 second pause between requests to respect rate limits

### Gear / Shoe Tracker *(new)*
Automatic aggregation of mileage per shoe/gear item set on Strava:
- **Per-gear cards** — one card per shoe with: total km, run count, average pace, first and last use date
- **Progress bar** — visual fill toward a configurable replacement threshold per shoe (default 700 km)
- **Status badge** — ✓ OK (< 80%), → Near limit (80–100%), ⚠ Replace soon (> 100%)
- **Editable threshold** — inline text field and Save button per shoe; value persisted in MongoDB
- **Monthly usage chart** — stacked bar chart of the last 12 months, one color per gear item
- Gear data is read directly from Strava activity downloads; if no gear is assigned on Strava a friendly empty-state message is shown

### Database
From the **Database** menu in the topbar:
- **Export ZIP** — exports all database activities to a `.zip` archive (one JSON file per run); useful as backup or to move the database to another machine
- **Import ZIP** — imports a previously exported `.zip` archive; activities already present are skipped (deduplication by Strava ID); new ones are saved to MongoDB
- **Runs heatmap** — generates an interactive map in the browser with all GPS polylines overlaid; dark CartoDB background, each track in semi-transparent orange; tooltip with name and date on hover

### Theme
The topbar includes a **☀ Light / 🌙 Dark** button to switch between dark theme (default, inspired by GitHub/Strava) and light theme. The preference is not saved between sessions.

### Export
From the **Export** menu:
- **PNG** — all five charts in high resolution (180 dpi) *(requires open activity)*
- **PDF** — 2-page report: text summary + splits + charts *(requires open activity)*
- **CSV Splits** — kilometer-by-kilometer splits *(requires open activity)*
- **GPX** — exports the GPS track in standard GPX format, compatible with Garmin, Komoot, etc. *(requires open activity with GPS data)*
- **CSV Statistics** — exports monthly statistics (km, runs, time, pace, elevation) to CSV for external analysis (Excel, etc.)

---

## Technical Architecture

```
strava_viewer/
├── main.py                  # Entry point — starts StravaApp
├── config.py                # Constants: colors, Strava URLs, MongoDB parameters
├── interval_detector.py     # Interval detection algorithm (pure Python, no UI deps)
├── models.py                # ActivityData class — Strava JSON parsing, computed properties
├── storage.py               # MongoStorage — activity save/read on MongoDB
├── storage_manager.py       # Facade: manages MongoDB connection and Docker startup
├── downloader.py            # OAuth2 Strava, download activity list and details
├── docker-compose.yml       # MongoDB 7 on port 27017 (automatic startup)
└── ui/
    ├── __init__.py
    ├── app.py               # StravaApp (tk.Tk) — main window, sidebar, menu
    ├── widgets.py           # Reusable widgets: StatCard, make_scrollable, embed_mpl…
    ├── downloader_ui.py     # Modal download window from Strava
    ├── export_pdf.py        # 2-page PDF generation with matplotlib PdfPages
    ├── tab_calendar.py      # Monthly Calendar tab
    ├── tab_dashboard.py     # Dashboard tab
    ├── tab_charts.py        # Charts tab + _build_export_fig() for PNG/PDF
    ├── tab_hr.py            # HR Zones tab
    ├── tab_map.py           # Map tab (opens external browser)
    ├── tab_gear.py          # Gear / Shoe Tracker tab
    ├── tab_splits.py        # Splits tab
    ├── tab_intervals.py     # Interval Detection tab
    ├── tab_best.py          # Best Efforts tab
    ├── tab_compare.py       # Compare tab
    ├── tab_library.py       # Library tab with pagination
    ├── tab_stats.py         # Global Statistics tab
    └── tab_raw.py           # Raw JSON tab
```

### Storage
The application uses **MongoDB** as the sole storage backend, managed by `StorageManager`. The connection is attempted at startup in a background thread; if MongoDB is unavailable the Library and Statistics will be empty until connected.

### MongoDB Connection
`StorageManager.connect_mongo(auto_start=True)` attempts:
1. Direct connection to `localhost:27017`
2. If it fails, runs `docker compose up -d` and retries 5 times (3s interval)

The connection status is visible in the topbar (● green = connected, ○ gray = offline). Clicking the indicator allows manual enable/disable.

### OAuth2 Strava
The OAuth2 flow in `downloader.py`:
1. Opens the browser on the Strava authorization form
2. Starts a local HTTP server on `localhost:8765` in a daemon thread
3. Captures the authorization code from the redirect
4. Exchanges the code for access token + refresh token
5. Saves the token in `.strava_token.json` (automatic renewal on expiry)

---

## Requirements

- **Python 3.10+**
- **Docker Desktop** (optional, only for MongoDB)

### Python Dependencies

```
pip install requests folium matplotlib numpy pymongo tkinterweb
```

| Library | Usage |
|---|---|
| `requests` | Strava API calls |
| `folium` | HTML map generation |
| `matplotlib` | Charts, PNG/PDF export |
| `numpy` | Power law fit and Monte Carlo simulation (performance curve + race prediction) |
| `pymongo` | MongoDB connection |
| `tkinter` | GUI (included in standard Python) |

---

## Startup

```bash
python main.py
```

---

## Configuration

All parameters are in `config.py`:

```python
# MongoDB
MONGO_URI        = "mongodb://localhost:27017"
MONGO_DB         = "strava"
MONGO_COLLECTION = "activities"

# OAuth Strava token saved in
STRAVA_TOKEN_FILE = ".strava_token.json"

# Maximum activities in comparison
MAX_COMPARE = 5
```

### Configuring the Strava app (first access)

1. Go to [https://www.strava.com/settings/api](https://www.strava.com/settings/api)
2. Create a new application
3. Set **Authorization Callback Domain** to `localhost`
4. Copy **Client ID** and **Client Secret**
5. In the app click **Download from Strava**, enter credentials and click **▶ START DOWNLOAD**
6. The browser will open for authorization — log in and authorize
7. The download will start automatically
8. It may be necessary to restart the procedure in subsequent days due to rate limits imposed by Strava

> **Note:** To download GPS polylines (required for the map) the app requires the `activity:read_all` scope. Strava requests it automatically during authorization.

### MongoDB with Docker

If Docker Desktop is installed, MongoDB starts automatically on the first app launch. Alternatively you can start it manually:

```bash
docker compose up -d
```

To stop it:

```bash
docker compose down
```

MongoDB data is saved in a persistent Docker volume and survives restarts.

---

## Operational Notes

- The first time runs are downloaded, the browser is opened for Strava authentication; in subsequent sessions the token is renewed automatically without opening the browser
- Download is incremental: runs already present in the database are skipped automatically
- The GPS map requires an internet connection to load tiles in the browser (CartoDB, OpenStreetMap, Esri Satellite)
- PDF export requires `matplotlib` installed
- The heatmap requires an internet connection to load CartoDB tiles in the browser

### Files not tracked by git

| File | Content |
|---|---|
| `.strava_token.json` | Strava OAuth token (access + refresh token) |

## AI Usage

- The application was entirely built using Claude Code AI with the Sonnet 4.6 model
