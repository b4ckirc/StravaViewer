# ⬡ Strava Viewer 3.0

Desktop-Anwendung zum Analysieren, Visualisieren und Vergleichen von Laufaktivitäten, die von Strava heruntergeladen wurden. Native grafische Benutzeroberfläche (tkinter), Hell-/Dunkel-Theme und MongoDB als einziges Speicher-Backend.

---

> Wenn dieses Projekt nützlich für Sie ist und Sie dem Entwickler einen virtuellen Kaffee spendieren möchten, können Sie das hier tun → [☕ PayPal](https://paypal.me/TeoVr81). Kein Druck — jeder km zählt, Spende oder nicht.

---

## Funktionen

### Aktivitäten öffnen
- Laden Sie alle Ihre Läufe direkt von Strava herunter mit der Schaltfläche **Von Strava herunterladen** — Aktivitäten werden in MongoDB gespeichert

### Dashboard
Vollständige Übersicht der geöffneten Aktivität:
- Distanz, aktive/Gesamtzeit, Durchschnitts- und Besttempo, Geschwindigkeit
- Positives und negatives Höhenprofil
- Durchschnittliche und maximale Herzfrequenz, Kadenz, Kalorien
- Leistungsindizes (Suffer Score, VAM, usw.)

### Diagramme
Fünf in die Benutzeroberfläche eingebettete Diagramme:
- **Tempo pro km** — farbige Balken (grün = schneller als Durchschnitt, blau = Durchschnitt, rot = langsamer)
- **Geschwindigkeit** — Linie mit gefülltem Bereich
- **Höhenprofil** — Balkendiagramm
- **Herzfrequenz** — Zeitreihenlinie
- **Kadenz** — Verlauf pro Kilometer

### HF-Zonen
- Manuelle Einstellung der maximalen Herzfrequenz
- Zeitverteilung pro Zone (Z1–Z5) mit farbigen horizontalen Balken
- HF vs. Tempo-Streudiagramm mit Trendlinie und Zonenbändern

### GPS-Karte
Die Karte öffnet sich im **Standardbrowser** (Chrome, Edge, Firefox…) und enthält:

- **Layer-Auswahl** — vier auswählbare Hintergründe über das Panel oben rechts:
  - *Dunkel* (CartoDB dark matter, Standard)
  - *OpenStreetMap*
  - *Satellit* (Esri WorldImagery, echte Satellitenbilder, kein API-Schlüssel erforderlich)
  - *Hell* (CartoDB positron)
- **Tempofarben-Strecke** — die Polylinie ist km für km mit einem Grün → Gelb → Rot-Verlauf aufgeteilt (grün = schnellster km, rot = langsamster km); beim Hovern über jeden Abschnitt erscheint ein Tooltip mit Tempo, HF und Höhenunterschied des km
- **Kilometermarkierungen** — ein nummerierter Indikator für jeden abgeschlossenen km; ein Klick öffnet ein Popup mit Tempo, durchschnittlicher HF und Höhenunterschied dieses Kilometers
- **Erweiterte Start-/Ziel-Popups** — grüner (Start) und roter (Ziel) Marker mit vollständigen Popups: Datum, Distanz, Zeit, Durchschnitts-/Besttempo, HF, Höhenunterschied, Kalorien, Suffer Score
- **Statistik-Overlay** — feste Leiste oben auf der Karte mit den wichtigsten Aktivitätsmetriken (Name, Distanz, Zeit, Tempo, HF, Höhenunterschied)
- **Vollbild-Schaltfläche** — erweitert die Karte auf den ganzen Bildschirm im Browser
- **MiniMap** — 150×150 Übersichtskarte in der unteren rechten Ecke zur Orientierung beim Zoomen; umschaltbar

Erfordert die Strava-Berechtigung `activity:read_all` für die GPS-Polylinie und eine Internetverbindung zum Laden der Kacheln im Browser.

### Splits
Scrollbare Tabelle mit Kilometer-für-Kilometer-Daten:
- Distanz, Zeit, Tempo, Geschwindigkeit, HF, Höhenunterschied, Kadenz
- Tempofarbe zur sofortigen Identifizierung der schnellsten/langsamsten km

### Intervallerkennung *(neu)*
Automatische Erkennung und Analyse strukturierter Intervalltrainings aus den km-Splittdaten:
- **Automatische Erkennung** — der Algorithmus berechnet Mittelwert und Standardabweichung des Tempos und klassifiziert jeden km als *schnell*, *langsam* oder *neutral* mit einem ±0,5σ-Schwellenwert; benötigt mindestens 3 schnelle Segmente und einen Variationskoeffizienten ≥ 6%
- **Trainingsklassifizierung** — identifiziert automatisch den Sitzungstyp: *VO₂max-Intervalle*, *Schwellen-Intervalle*, *Tempo / Progressiv*, *Fartlek*, *Leichte Strides*
- **Analytik-Leiste** — 4 StatCards: Durchschnittstempo Arbeit, Durchschnittstempo Erholung, Fade Rate (letztes vs. erstes Intervall), Konsistenz-Score (0–100)
- **Segmenttabelle** — scrollbare Liste aller erkannten Segmente mit Typ (⚡ Arbeit / ○ Erholung), Distanz, Zeit, Tempo, HF und Delta vs. Durchschnitt; Arbeitsintervalle werden mit orangem linken Rand hervorgehoben
- **Diagramme** — Balkendiagramm des Tempos pro Segment (orange = Arbeit, blau = Erholung) mit Referenzlinien; HF-Liniendiagramm pro Segment wenn vorhanden
- Für Nicht-Intervall-Einheiten wird eine klare Meldung „Kein Intervalltraining" mit Gleichmäßigkeitsstatistiken angezeigt

### Bestleistungen
Liste der von Strava erkannten Bestleistungen (1 km, 5 km, 10 km, Halbmarathon, Marathon usw.) mit 🏆-Abzeichen für persönliche Rekorde.

### Vergleich
Seitenweiser Vergleich von bis zu 5 Aktivitäten:
- Vergleichstabelle mit grüner (beste) und roter (schlechteste) Hervorhebung für jede Metrik
- Überlagerte km-für-km-Tempokurve
- Überlagerte Herzfrequenzkurve
- Aktivitäten aus dem Bibliothek-Tab mit der Schaltfläche ➕ hinzufügen

### Bibliothek
Liste aller in der Datenbank gespeicherten Läufe, mit:
- **Seitennummerierung** — 100 Zeilen pro Seite mit ◀ ▶ Navigation
- **Filter** nach Name/Beschreibung, Distanz (min–max km), Datumsbereich und **Nur Rennen** (filtert Aktivitäten mit `workout_type = race`)
- **Semantische** Tempofarbe: grün < 5:00/km, gelb < 6:30/km, rot darüber
- Zeilen-Hover mit visueller Hervorhebung
- Aktivität öffnen mit 📂, zum Vergleich hinzufügen mit ➕, löschen mit 🗑
- Anzeige des MongoDB-Verbindungsstatus

### Kalender
Monatsansicht aller Läufe mit Monat-für-Monat-Navigation:
- Jede Zelle mit einem Lauf zeigt Distanz, Tempo und Herzfrequenz; die Intensität der orangefarbenen Farbe ist **proportional zu den zurückgelegten km** im Vergleich zum längsten Tag des Monats (Heatmap)
- Tage mit mehreren Läufen zeigen einen zusätzlichen Zähler mit ◀ ▶ Schaltflächen zum Durchblättern der Läufe desselben Tages
- ◀ ▶ Schaltflächen zur Navigation zwischen den Monaten, "Heute" um zum aktuellen Monat zurückzukehren
- Klick auf eine Zelle öffnet die Aktivität im Dashboard-Tab
- Die Gesamt-km und Anzahl der Läufe des Monats wird in der Kopfzeile angezeigt

### Statistiken
Aggregierte Statistiken über **alle** Läufe in der Datenbank (ignoriert Filter und Seitennummerierung):
- **Jahresziel** — legen Sie ein km-Ziel für das laufende Jahr mit Fortschrittsbalken fest; der Wert wird in `settings.json` gespeichert und zwischen Sitzungen gespeichert
- Summen: Läufe, km, Stunden, Höhenunterschied, Durchschnittstempo, Durchschnitts-HF, Kalorien, km/Woche
- **Aktivitäts-Heatmap** — GitHub-Stil-Kalenderraster der letzten 52 Wochen (Zeilen = Wochentage Mo→So, Spalten = Wochen): jede Zelle ist orange gefärbt mit Intensität proportional zu den an diesem Tag gelaufenen km, dunkelgrau bei Ruhetagen; Farbskalabalken unten; Tooltip beim Hovern mit Datum und km
- **Athletisches Profil** — hexagonales Radardiagramm mit 6 normalisierten 0–100 Dimensionen: *Geschwindigkeit* (Durchschnittstempo, Skala 8:20→3:20/km), *Ausdauer* (Median der Distanzen, Skala 3→42 km), *Höhenunterschied* (Durchschnitt m↑/km, Skala 0→40 m/km), *Konstanz* (% Wochen mit mindestens einem Lauf in den letzten 52), *Volumen* (Durchschnitt km/Woche in den letzten 52, Skala 0→70), *Progression* (Vergleich Durchschnittstempo letzte 3 Monate vs. vorherige 3 Monate); neben einem Panel mit numerischen Wertungen, proportionalen Balken und Beschreibung jeder Dimension
- **Monatstabelle** — letzte 12 Monate mit km, Läufen, Zeit, Durchschnittstempo, Höhenunterschied; Balkendiagramm km pro Monat
- Jahrestabelle mit km, Läufen, Zeit, Durchschnittstempo, Höhenunterschied; km pro Jahr und Läufe pro Jahr-Diagramm
- Distanzverteilung (Kuchendiagramm)
- **Trainingsbelastung** — ATL/CTL/TSB-Diagramm (Banister TRIMP) der letzten 12 Monate:
  - *CTL (Fitness)* — exponentiell gewichteter Durchschnitt über 42 Tage
  - *ATL (Ermüdung)* — exponentiell gewichteter Durchschnitt über 7 Tage
  - *TSB (Form)* — CTL − ATL (positiv = ausgeruht, negativ = ermüdet)
- **Persönliche Rekorde** — Tabelle mit der besten persönlichen Zeit für kanonische Distanzen (1 km, 5 km, 10 km, Halbmarathon, Marathon), mit Aktivitätsname und Datum der Erzielung
- **Steigungsanalyse (Grade Analysis)** — Balkendiagramm des medianen Tempos aufgeteilt in 6 Gradientenbänder (von steilem Abstieg <−8% bis Anstieg >8%), berechnet aus 1-km-Splits von Strava aufgezeichnet; Filter "Letzte Tage" und "Nur Rennen"; Daten aus diesem Diagramm fließen in die individuelle Höhenkorrektur der Leistungsvorhersage ein; ℹ-Schaltfläche mit Leitfaden pro Band und Trainingsempfehlungen
- **Leistungskurve** — Log-Log-Diagramm Distanz vs. Zeit für Bestleistungen (von 400m bis Marathon) mit Potenzgesetz-Fit `t = A × d^b`; verwendete Zeiten sind `moving_time` (Pausen ausgeschlossen); Filter "Letzte Tage" und "Nur Rennen"; der Exponent `b` offenbart das athletische Profil (Sprinter vs. Langstreckenläufer, Vergleich mit Riegels b=1,06); ℹ-Schaltfläche mit Theorie und Interpretationsleitfaden
- **Leistungsvorhersage (Monte Carlo)** — Schätzung der Zeit über beliebige Distanzen mit Simulation von 5000 Szenarien; konfigurierbare Parameter: Zieldistanz (standard oder benutzerdefiniert in km), positiver Höhenunterschied der Strecke, historisches Zeitfenster (letzte N Tage), minimale und maximale Länge der Läufe zum Abrufen der Bestleistungen (min/max km), Nur-Rennen-Filter; die Höhenkorrektur ist individualisiert: berechnet durch lineare Regression auf Ihren echten Splits (Sek/km pro 1% Steigung), mit Fallback auf das Minetti-Modell bei unzureichenden Daten; das Ergebnis ist ein Histogramm mit P10/P25/P50/P75/P90 Perzentilen und einem Diagnosepanel mit den beim Fit verwendeten Daten, dem b-Koeffizient und der rohen Basiszeit; ℹ-Schaltfläche mit vollständigem Leitfaden zu Parametern, Berechnung und Ergebnisinterpretation
- **Rennanalyse und VDOT** — analysiert alle als "Rennen" auf Strava klassifizierten Aktivitäten (`workout_type = 1`) und berechnet für jede den VDOT nach Jack Daniels' Formel (Index der aeroben Kapazität aus tatsächlicher Distanz und Zeit, ohne Labortest); zeigt drei Statistik-Karten (Gesamtrennen, bester VDOT, neuester VDOT), ein Liniendiagramm der VDOT-Entwicklung über die Zeit mit gestrichelter Linie beim historischen Maximum, eine paginierte Renntabelle (10 pro Seite, anklickbar zum Öffnen der Aktivität) mit Datum, km, Zeit, VDOT und Name, und eine Vorhersagetabelle für 1K / 5K / 10K / Halbmarathon / Marathon berechnet aus dem VDOT des zuletzt aufgezeichneten Rennens; ℹ-Schaltfläche mit Formerklärung, Referenzwerttabelle (Anfänger → Elite) und Leitfaden zur Interpretation der Vorhersagen
- **Wiederkehrende Strecken** — erkennt automatisch Strecken, die Sie mindestens 3 Mal gelaufen sind, indem Aktivitäten nach Startbereich (~300 m) und Distanz (±1 km) gruppiert werden; für jede Gruppe wird angezeigt: scrollbare Liste mit häufigstem Namen, Distanz, Anzahl der Läufe, Zeitraum und Stadt/Koordinaten; Streudiagramm des Tempos im Zeitverlauf mit Grün→Rot-Färbung (schneller→langsamer), gestrichelte Trendlinie, Hervorhebung des besten Laufs und des letzten; Kopfzeile mit bestem Tempo, Durchschnittstempo und Trendindikator (verbessert/verschlechtert/stabil); Liste der Gruppenläufe mit Datum, km, Tempo, HF und Name, anklickbar zum Öffnen der Aktivität; die Stadt wird zunächst aus Strava-Metadaten abgerufen, dann über Nominatim-Reverse-Geocoding (OpenStreetMap) mit persistentem Cache auf MongoDB, sequentieller Thread mit 1 Sekunde Pause zwischen Anfragen zur Einhaltung der Rate-Limits

### Datenbank
Aus dem **Datenbank**-Menü in der Topbar:
- **ZIP exportieren** — exportiert alle Datenbankaktivitäten in ein `.zip`-Archiv (eine JSON-Datei pro Lauf); nützlich als Backup oder zum Verschieben der Datenbank auf einen anderen Rechner
- **ZIP importieren** — importiert ein zuvor exportiertes `.zip`-Archiv; bereits vorhandene Aktivitäten werden übersprungen (Deduplizierung nach Strava-ID); neue werden in MongoDB gespeichert
- **Läufe-Heatmap** — generiert eine interaktive Karte im Browser mit allen überlagerten GPS-Polylinien; dunkler CartoDB-Hintergrund, jede Strecke in halbtransparentem Orange; Tooltip mit Name und Datum beim Hovern

### Theme
Die Topbar enthält eine Schaltfläche **☀ Hell / 🌙 Dunkel** zum Wechseln zwischen dunklem Theme (Standard, inspiriert von GitHub/Strava) und hellem Theme. Die Einstellung wird nicht zwischen Sitzungen gespeichert.

### Export
Aus dem **Exportieren**-Menü:
- **PNG** — alle fünf Diagramme in hoher Auflösung (180 dpi) *(erfordert geöffnete Aktivität)*
- **PDF** — 2-seitiger Bericht: Textzusammenfassung + Splits + Diagramme *(erfordert geöffnete Aktivität)*
- **CSV Splits** — Kilometer-für-Kilometer-Splits *(erfordert geöffnete Aktivität)*
- **GPX** — exportiert die GPS-Strecke im Standard-GPX-Format, kompatibel mit Garmin, Komoot usw. *(erfordert geöffnete Aktivität mit GPS-Daten)*
- **CSV Statistiken** — exportiert monatliche Statistiken (km, Läufe, Zeit, Tempo, Höhenunterschied) als CSV für externe Analysen (Excel usw.)

---

## Technische Architektur

```
strava_viewer/
├── main.py                  # Einstiegspunkt — startet StravaApp
├── config.py                # Konstanten: Farben, Strava-URLs, MongoDB-Parameter
├── interval_detector.py     # Intervallerkennung-Algorithmus (reines Python, keine UI-Abhängigkeiten)
├── models.py                # ActivityData-Klasse — Strava-JSON-Parsing, berechnete Eigenschaften
├── storage.py               # MongoStorage — Aktivitätsspeicherung/-lesung auf MongoDB
├── storage_manager.py       # Fassade: verwaltet MongoDB-Verbindung und Docker-Start
├── downloader.py            # OAuth2 Strava, Download Aktivitätsliste und Details
├── docker-compose.yml       # MongoDB 7 auf Port 27017 (automatischer Start)
└── ui/
    ├── __init__.py
    ├── app.py               # StravaApp (tk.Tk) — Hauptfenster, Seitenleiste, Menü
    ├── widgets.py           # Wiederverwendbare Widgets: StatCard, make_scrollable, embed_mpl…
    ├── downloader_ui.py     # Modales Download-Fenster von Strava
    ├── export_pdf.py        # 2-seitige PDF-Generierung mit matplotlib PdfPages
    ├── tab_calendar.py      # Monatlicher Kalender-Tab
    ├── tab_dashboard.py     # Dashboard-Tab
    ├── tab_charts.py        # Diagramme-Tab + _build_export_fig() für PNG/PDF
    ├── tab_hr.py            # HF-Zonen-Tab
    ├── tab_map.py           # Karten-Tab (öffnet externen Browser)
    ├── tab_splits.py        # Splits-Tab
    ├── tab_intervals.py     # Intervallerkennung-Tab
    ├── tab_best.py          # Bestleistungen-Tab
    ├── tab_compare.py       # Vergleichs-Tab
    ├── tab_library.py       # Bibliotheks-Tab mit Seitennummerierung
    ├── tab_stats.py         # Globaler Statistiken-Tab
    └── tab_raw.py           # Roh-JSON-Tab
```

### Speicherung
Die Anwendung verwendet **MongoDB** als einziges Speicher-Backend, verwaltet von `StorageManager`. Die Verbindung wird beim Start in einem Hintergrund-Thread hergestellt; falls MongoDB nicht verfügbar ist, bleiben Bibliothek und Statistiken bis zur Verbindung leer.

### MongoDB-Verbindung
`StorageManager.connect_mongo(auto_start=True)` versucht:
1. Direkte Verbindung zu `localhost:27017`
2. Bei Fehler wird `docker compose up -d` ausgeführt und 5 Mal wiederholt (3s Intervall)

Der Verbindungsstatus ist in der Topbar sichtbar (● grün = verbunden, ○ grau = offline). Durch Klicken auf den Indikator kann manuell aktiviert/deaktiviert werden.

### OAuth2 Strava
Der OAuth2-Ablauf in `downloader.py`:
1. Öffnet den Browser auf dem Strava-Autorisierungsformular
2. Startet einen lokalen HTTP-Server auf `localhost:8765` in einem Daemon-Thread
3. Erfasst den Autorisierungscode aus der Weiterleitung
4. Tauscht den Code gegen Access-Token + Refresh-Token
5. Speichert das Token in `.strava_token.json` (automatische Erneuerung bei Ablauf)

---

## Anforderungen

- **Python 3.10+**
- **Docker Desktop** (optional, nur für MongoDB)

### Python-Abhängigkeiten

```
pip install requests folium matplotlib numpy pymongo tkinterweb
```

| Bibliothek | Verwendung |
|---|---|
| `requests` | Strava-API-Aufrufe |
| `folium` | HTML-Karten-Generierung |
| `matplotlib` | Diagramme, PNG/PDF-Export |
| `numpy` | Potenzgesetz-Fit und Monte-Carlo-Simulation (Leistungskurve + Rennvorhersage) |
| `pymongo` | MongoDB-Verbindung |
| `tkinter` | Grafische Benutzeroberfläche (in Standard-Python enthalten) |

---

## Start

```bash
python main.py
```

---

## Konfiguration

Alle Parameter befinden sich in `config.py`:

```python
# MongoDB
MONGO_URI        = "mongodb://localhost:27017"
MONGO_DB         = "strava"
MONGO_COLLECTION = "activities"

# OAuth Strava-Token gespeichert in
STRAVA_TOKEN_FILE = ".strava_token.json"

# Maximale Aktivitäten im Vergleich
MAX_COMPARE = 5
```

### Strava-App konfigurieren (erster Zugang)

1. Gehen Sie zu [https://www.strava.com/settings/api](https://www.strava.com/settings/api)
2. Erstellen Sie eine neue Anwendung
3. Setzen Sie **Authorization Callback Domain** auf `localhost`
4. Kopieren Sie **Client ID** und **Client Secret**
5. Klicken Sie in der App auf **Von Strava herunterladen**, geben Sie die Anmeldedaten ein und klicken Sie auf **▶ DOWNLOAD STARTEN**
6. Der Browser öffnet sich zur Autorisierung — anmelden und autorisieren
7. Der Download startet automatisch
8. Es kann notwendig sein, das Verfahren in den folgenden Tagen aufgrund der von Strava auferlegten Rate-Limits neu zu starten

> **Hinweis:** Um GPS-Polylinien herunterzuladen (für die Karte erforderlich), benötigt die App den Scope `activity:read_all`. Strava fordert ihn automatisch während der Autorisierung an.

### MongoDB mit Docker

Wenn Docker Desktop installiert ist, startet MongoDB automatisch beim ersten Start der App. Alternativ können Sie es manuell starten:

```bash
docker compose up -d
```

Zum Stoppen:

```bash
docker compose down
```

MongoDB-Daten werden in einem persistenten Docker-Volume gespeichert und überleben Neustarts.

---

## Betriebshinweise

- Beim ersten Download von Läufen wird der Browser für die Strava-Authentifizierung geöffnet; in nachfolgenden Sitzungen wird das Token automatisch erneuert, ohne den Browser zu öffnen
- Der Download ist inkrementell: bereits in der Datenbank vorhandene Läufe werden automatisch übersprungen
- Die GPS-Karte benötigt eine Internetverbindung zum Laden der Kacheln im Browser (CartoDB, OpenStreetMap, Esri Satellite)
- Der PDF-Export erfordert installiertes `matplotlib`
- Die Heatmap benötigt eine Internetverbindung zum Laden der CartoDB-Kacheln im Browser

### Von git nicht verfolgte Dateien

| Datei | Inhalt |
|---|---|
| `.strava_token.json` | Strava OAuth-Token (Access + Refresh Token) |
| `settings.json` | Lokale Benutzereinstellungen (z. B. jährliches km-Ziel) |

## KI-Nutzung

- Die Anwendung wurde vollständig mit der KI Claude Code mit dem Sonnet 4.6 Modell entwickelt
