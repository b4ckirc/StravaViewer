# ── config.py ─────────────────────────────────────────────────────────────────
# Global application constants

APP_NAME    = "Strava Activity Viewer"
APP_VERSION = "3.0"
MAX_COMPARE = 5   # maximum activities in comparison

# UI color palette (dark Strava-inspired theme)
C = {
    "bg":       "#0d1117",
    "surface":  "#161b22",
    "surface2": "#21262d",
    "border":   "#30363d",
    "accent":   "#fc4c02",
    "accent2":  "#ff8c69",
    "text":     "#e6edf3",
    "text_dim": "#8b949e",
    "green":    "#3fb950",
    "blue":     "#58a6ff",
    "purple":   "#bc8cff",
    "yellow":   "#d29922",
    "red":      "#f85149",
    "orange":   "#f0883e",
}

# Immutable copy of dark theme (used for restore)
C_DARK = dict(C)

# Light theme palette (for future theme switching)
C_LIGHT = {
    "bg":       "#f0f2f5",
    "surface":  "#ffffff",
    "surface2": "#e2e8f0",
    "border":   "#c4cdd6",
    "accent":   "#fc4c02",
    "accent2":  "#d43d00",
    "text":     "#1c2128",
    "text_dim": "#57606a",
    "green":    "#1a7f37",
    "blue":     "#0969da",
    "purple":   "#6e40c9",
    "yellow":   "#7d6514",
    "red":      "#cf222e",
    "orange":   "#953800",
}

# Current theme state ("dark" or "light") — mutable list for shared reference
_current_theme = ["dark"]

# Colors for multiple comparison
COMPARE_COLORS  = ["#58a6ff", "#fc4c02", "#3fb950", "#bc8cff", "#d29922"]
COMPARE_MARKERS = ["o", "s", "^", "D", "P"]
COMPARE_EMOJIS  = ["🔵", "🟠", "🟢", "🟣", "🟡"]

# Zone HR (% FC max, nome, colore)
HR_ZONES = [
    ("Z1 Recupero",    0,  60, "#4a9eff"),
    ("Z2 Aerobica",   60,  70, "#3fb950"),
    ("Z3 Soglia",     70,  80, "#d29922"),
    ("Z4 Anaerobica", 80,  90, "#f0883e"),
    ("Z5 Massimale",  90, 100, "#f85149"),
]

# MongoDB / Docker
MONGO_HOST      = "localhost"
MONGO_PORT      = 27017
MONGO_DB        = "strava"
MONGO_COLL      = "activities"
DOCKER_COMPOSE  = "docker-compose.yml"

# Strava OAuth
STRAVA_AUTH_URL    = "https://www.strava.com/oauth/authorize"
STRAVA_TOKEN_URL   = "https://www.strava.com/oauth/token"
STRAVA_API_BASE    = "https://www.strava.com/api/v3"
STRAVA_REDIRECT    = "http://localhost:8765/callback"
STRAVA_TOKEN_FILE  = ".strava_token.json"
