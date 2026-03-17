# ── downloader.py ─────────────────────────────────────────────────────────────
"""
Strava OAuth2 authentication and running activity download.
"""

import os, json, time, webbrowser, urllib.parse, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from config import (STRAVA_AUTH_URL, STRAVA_TOKEN_URL, STRAVA_API_BASE,
                    STRAVA_REDIRECT, STRAVA_TOKEN_FILE)
from i18n import t

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
            title = t("dl_oauth_html_title")
            body  = t("dl_oauth_html_body")
            html  = (
                f'<html><body style="font-family:sans-serif;'
                f'text-align:center;padding:60px;background:#0d1117;color:#e6edf3">'
                f'<h2 style="color:#fc4c02">{title}</h2>'
                f'<p>{body}</p>'
                f'</body></html>'
            )
            self.wfile.write(html.encode("utf-8"))
            _auth_event.set()
        else:
            self.send_response(400)
            self.end_headers()
            _auth_event.set()

    def log_message(self, *a): pass


def _get_auth_code(client_id: str, progress_cb=None) -> str:
    """Starts the OAuth server in a separate thread and opens the browser."""
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

    # HTTP server in daemon thread — does not block the UI
    server = HTTPServer(("localhost", 8765), _OAuthHandler)
    server.timeout = 1

    def _serve():
        while not _auth_event.is_set():
            server.handle_request()
        server.server_close()

    srv_thread = threading.Thread(target=_serve, daemon=True)
    srv_thread.start()

    if progress_cb:
        progress_cb(t("dl_oauth_open_browser"))
        progress_cb(t("dl_oauth_authorize"))
    webbrowser.open(url)

    # Wait for callback (max 3 minutes)
    _auth_event.wait(timeout=180)

    if not _auth_code:
        raise RuntimeError(t("dl_oauth_timeout"))
    return _auth_code


def load_token(mongo_storage=None) -> dict | None:
    if mongo_storage is not None:
        return mongo_storage.load_token()
    if os.path.exists(STRAVA_TOKEN_FILE):
        with open(STRAVA_TOKEN_FILE) as f:
            return json.load(f)
    return None

def save_token(token: dict, mongo_storage=None):
    if mongo_storage is not None:
        mongo_storage.save_token(token)
    else:
        with open(STRAVA_TOKEN_FILE, "w") as f:
            json.dump(token, f, indent=2)


def get_access_token(client_id: str, client_secret: str, progress_cb=None,
                     mongo_storage=None) -> str:
    if not HAS_REQUESTS:
        raise RuntimeError(t("dl_requests_missing"))

    token = load_token(mongo_storage)

    # Valid token
    if token and token.get("expires_at", 0) > time.time() + 60:
        if progress_cb:
            progress_cb(t("dl_token_valid"))
        return token["access_token"]

    # Refresh
    if token and "refresh_token" in token:
        if progress_cb:
            progress_cb(t("dl_token_refreshing"))
        r = _requests.post(STRAVA_TOKEN_URL, data={
            "client_id":     client_id,
            "client_secret": client_secret,
            "grant_type":    "refresh_token",
            "refresh_token": token["refresh_token"],
        }, timeout=15)
        r.raise_for_status()
        token = r.json()
        save_token(token, mongo_storage)
        if progress_cb:
            progress_cb(t("dl_token_refreshed"))
        return token["access_token"]

    # First login — OAuth via browser
    code = _get_auth_code(client_id, progress_cb)
    if progress_cb:
        progress_cb(t("dl_oauth_exchanging"))
    r = _requests.post(STRAVA_TOKEN_URL, data={
        "client_id":     client_id,
        "client_secret": client_secret,
        "code":          code,
        "grant_type":    "authorization_code",
    }, timeout=15)
    r.raise_for_status()
    token = r.json()
    save_token(token, mongo_storage)
    athlete = token.get("athlete", {})
    if progress_cb:
        name = f"{athlete.get('firstname', '')} {athlete.get('lastname', '')}".strip()
        progress_cb(t("dl_authenticated_as").format(name=name))
    return token["access_token"]


# ── Download activities ────────────────────────────────────────────────────────

def fetch_activity_list(access_token: str, progress_cb=None) -> list[dict]:
    """Downloads the list of all running activities (summary)."""
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
                progress_cb(t("dl_rate_limit").format(wait=wait))
            time.sleep(wait)
            continue
        r.raise_for_status()
        acts = r.json()
        if not acts:
            break
        runs = [a for a in acts if a.get("type") == "Run" or a.get("sport_type") == "Run"]
        all_runs.extend(runs)
        if progress_cb:
            progress_cb(t("dl_page_progress").format(page=page, count=len(runs), total=len(all_runs)))
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
