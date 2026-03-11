# ── downloader.py ─────────────────────────────────────────────────────────────
"""
Autenticazione OAuth2 Strava e download attività di corsa.
"""

import os, json, time, webbrowser, urllib.parse, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from config import (STRAVA_AUTH_URL, STRAVA_TOKEN_URL, STRAVA_API_BASE,
                    STRAVA_REDIRECT, STRAVA_TOKEN_FILE)

try:
    import requests as _requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# ── OAuth ──────────────────────────────────────────────────────────────────────

_auth_code  = None
_auth_event = threading.Event()

class _OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global _auth_code
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if "code" in params:
            _auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"""<html><body style="font-family:sans-serif;
                text-align:center;padding:60px;background:#0d1117;color:#e6edf3">
                <h2 style="color:#fc4c02">&#10003; Autenticazione completata!</h2>
                <p>Puoi chiudere questa finestra e tornare all'applicazione.</p>
                </body></html>""")
            _auth_event.set()
        else:
            self.send_response(400)
            self.end_headers()
            _auth_event.set()

    def log_message(self, *a): pass


def _get_auth_code(client_id: str, progress_cb=None) -> str:
    """Avvia il server OAuth in un thread separato e apre il browser."""
    global _auth_code, _auth_event
    _auth_code  = None
    _auth_event = threading.Event()

    params = {
        "client_id":       client_id,
        "redirect_uri":    STRAVA_REDIRECT,
        "response_type":   "code",
        "approval_prompt": "auto",
        "scope":           "read,activity:read_all",
    }
    url = STRAVA_AUTH_URL + "?" + urllib.parse.urlencode(params)

    # Server HTTP in thread daemon — non blocca la UI
    server = HTTPServer(("localhost", 8765), _OAuthHandler)
    server.timeout = 1

    def _serve():
        while not _auth_event.is_set():
            server.handle_request()
        server.server_close()

    t = threading.Thread(target=_serve, daemon=True)
    t.start()

    if progress_cb:
        progress_cb("🌐 Apertura browser per autenticazione Strava…")
        progress_cb("   Accedi e autorizza l'app, poi torna qui.")
    webbrowser.open(url)

    # Attendi il callback (max 3 minuti)
    _auth_event.wait(timeout=180)

    if not _auth_code:
        raise RuntimeError("Timeout autenticazione OAuth (3 minuti). Riprova.")
    return _auth_code


def load_token() -> dict | None:
    if os.path.exists(STRAVA_TOKEN_FILE):
        with open(STRAVA_TOKEN_FILE) as f:
            return json.load(f)
    return None

def save_token(token: dict):
    with open(STRAVA_TOKEN_FILE, "w") as f:
        json.dump(token, f, indent=2)


def get_access_token(client_id: str, client_secret: str, progress_cb=None) -> str:
    if not HAS_REQUESTS:
        raise RuntimeError("Installa requests: pip install requests")

    token = load_token()

    # Token valido
    if token and token.get("expires_at", 0) > time.time() + 60:
        if progress_cb:
            progress_cb("✅ Token esistente ancora valido, nessun login necessario.")
        return token["access_token"]

    # Refresh
    if token and "refresh_token" in token:
        if progress_cb:
            progress_cb("🔄 Rinnovo token di accesso…")
        r = _requests.post(STRAVA_TOKEN_URL, data={
            "client_id":     client_id,
            "client_secret": client_secret,
            "grant_type":    "refresh_token",
            "refresh_token": token["refresh_token"],
        }, timeout=15)
        r.raise_for_status()
        token = r.json()
        save_token(token)
        if progress_cb:
            progress_cb("✅ Token rinnovato.")
        return token["access_token"]

    # Primo accesso — OAuth via browser
    code = _get_auth_code(client_id, progress_cb)
    if progress_cb:
        progress_cb("🔑 Scambio codice OAuth con token di accesso…")
    r = _requests.post(STRAVA_TOKEN_URL, data={
        "client_id":     client_id,
        "client_secret": client_secret,
        "code":          code,
        "grant_type":    "authorization_code",
    }, timeout=15)
    r.raise_for_status()
    token = r.json()
    save_token(token)
    athlete = token.get("athlete", {})
    if progress_cb:
        progress_cb(f"✅ Autenticato come: {athlete.get('firstname','')} {athlete.get('lastname','')}")
    return token["access_token"]


# ── Download attività ──────────────────────────────────────────────────────────

def fetch_activity_list(access_token: str, progress_cb=None) -> list[dict]:
    """Scarica l'elenco di tutte le attività di corsa (summary)."""
    headers  = {"Authorization": f"Bearer {access_token}"}
    all_runs = []
    page     = 1

    while True:
        r = _requests.get(
            f"{STRAVA_API_BASE}/athlete/activities",
            headers=headers,
            params={"per_page": 200, "page": page},
            timeout=30,
        )
        if r.status_code == 429:
            wait = max(int(r.headers.get("X-RateLimit-Reset", time.time() + 60)) - int(time.time()), 5)
            if progress_cb:
                progress_cb(f"⏳ Rate limit Strava, attendo {wait}s…")
            time.sleep(wait)
            continue
        r.raise_for_status()
        acts = r.json()
        if not acts:
            break
        runs = [a for a in acts if a.get("type") == "Run" or a.get("sport_type") == "Run"]
        all_runs.extend(runs)
        if progress_cb:
            progress_cb(f"📄 Pagina {page}: {len(runs)} corse (tot. {len(all_runs)})")
        page += 1
        if len(acts) < 200:
            break

    return all_runs


def fetch_activity_detail(activity_id: int, access_token: str) -> dict:
    headers = {"Authorization": f"Bearer {access_token}"}
    while True:
        r = _requests.get(
            f"{STRAVA_API_BASE}/activities/{activity_id}",
            headers=headers,
            timeout=30,
        )
        if r.status_code == 429:
            if r.headers.get("X-RateLimit-Reset"):
                wait = max(int(r.headers["X-RateLimit-Reset"]) - int(time.time()), 5)
            else:
                wait = 60
            time.sleep(wait)
            continue
        r.raise_for_status()
        return r.json()


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cid = input("Client ID: ").strip()
    csc = input("Client Secret: ").strip()
    tok = get_access_token(cid, csc, print)
    runs = fetch_activity_list(tok, print)
    print(f"\n{len(runs)} corse trovate.")
