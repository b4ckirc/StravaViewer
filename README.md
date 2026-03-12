# ⬡ Strava Viewer 3.0

Applicazione desktop per analizzare, visualizzare e confrontare le attività di corsa scaricate da Strava. Interfaccia grafica nativa (tkinter), dark theme, supporto MongoDB e archiviazione locale JSON.

---

## Funzionalità

### Apertura attività
- Apri un singolo file JSON esportato da Strava tramite il pulsante **APRI FILE**
- Oppure scarica direttamente tutte le tue corse da Strava con **SCARICA DA STRAVA**

### Dashboard
Panoramica completa dell'attività aperta:
- Distanza, tempo attivo/totale, passo medio e migliore, velocità
- Dislivello positivo e negativo
- Frequenza cardiaca media e massima, cadenza, calorie
- Indici di performance (Suffer Score, VAM, ecc.)

### Grafici
Cinque grafici embedded nell'interfaccia:
- **Passo per km** — barre colorate (verde = più veloce della media, blu = nella media, rosso = più lento)
- **Velocità** — linea con area riempita
- **Elevazione** — grafico a barre
- **Frequenza cardiaca** — linea temporale
- **Cadenza** — andamento per chilometro

### Zone HR
- Impostazione manuale della frequenza cardiaca massima
- Distribuzione del tempo per zona (Z1–Z5) con barre orizzontali colorate
- Scatter plot HR vs passo con linea di tendenza e bande di zona

### Mappa GPS
La mappa si apre nel **browser predefinito** (Chrome, Edge, Firefox…) e include:

- **Layer switcher** — quattro sfondi selezionabili dal pannello in alto a destra:
  - *Dark* (CartoDB dark matter, default)
  - *OpenStreetMap*
  - *Satellite* (Esri WorldImagery, immagini satellitari reali, senza API key)
  - *Chiaro* (CartoDB positron)
- **Tracciato colorato per passo** — la polyline è spezzata km per km con un gradiente verde → giallo → rosso (verde = km più veloce, rosso = km più lento); passando il mouse su ogni segmento compare il tooltip con passo, FC e dislivello del km
- **Marker chilometrici** — un indicatore numerato per ogni km completato; cliccando si apre un popup con passo, FC media e dislivello di quel chilometro
- **Popup Start/End arricchiti** — marker verde (inizio) e rosso (fine) con popup completi: data, distanza, tempo, passo medio/massimo, FC, dislivello, calorie, Suffer Score
- **Overlay statistiche** — barra fissa in cima alla mappa con le metriche chiave dell'attività (nome, distanza, tempo, passo, FC, dislivello)
- **Pulsante FullScreen** — espande la mappa a tutto schermo nel browser
- **MiniMap** — mappa panoramica 150×150 nell'angolo in basso a destra per orientarsi durante lo zoom; togglable

Richiede il permesso Strava `activity:read_all` per la polyline GPS e una connessione internet per caricare i tile nel browser.

### Splits
Tabella scrollabile con i dati chilometro per chilometro:
- Distanza, tempo, passo, velocità, HR, dislivello, cadenza
- Colore del passo per identificare subito i km più veloci/lenti

### Best Efforts
Elenco dei migliori sforzi rilevati da Strava (1 km, 5 km, 10 km, mezza maratona, maratona, ecc.) con badge 🏆 per i record personali.

### Confronto
Confronto side-by-side di fino a 5 attività:
- Tabella comparativa con evidenziazione verde (migliore) e rosso (peggiore) per ogni metrica
- Grafico passo km per km sovrapposto
- Grafico frequenza cardiaca sovrapposto
- Aggiunta attività dal tab Libreria con il pulsante ➕

### Libreria
Elenco di tutte le corse salvate nel database, con:
- **Paginazione** — 100 righe per pagina con navigazione ◀ ▶
- **Filtri** per nome/descrizione, distanza (min–max km), intervallo di date, e **Solo gare** (filtra le attività con `workout_type = race`)
- Apertura attività con 📂, aggiunta al confronto con ➕, eliminazione con 🗑
- Indicatore della fonte dati attiva (MongoDB o File JSON)

### Statistiche
Statistiche aggregate su **tutte** le corse nel database (ignora filtri e paginazione):
- Totali: corse, km, ore, dislivello, passo medio, HR media, calorie, km/settimana
- Tabella per anno con km, corse, tempo, passo medio, dislivello
- Grafici: km per anno, corse per anno, distribuzione distanze (torta)
- **Record personali** — tabella con il miglior tempo personale per le distanze canoniche (1 km, 5 km, 10 km, Mezza Maratona, Maratona), con nome attività e data in cui è stato realizzato

### Database
Dal menu **DATABASE** nella topbar:
- **Esporta ZIP** — esporta tutte le attività del database in un archivio `.zip` (file JSON per ogni corsa); utile come backup o per spostare il database su un'altra macchina
- **Importa ZIP** — importa un archivio `.zip` precedentemente esportato; le attività già presenti vengono saltate (deduplicazione per Strava ID); le nuove vengono salvate su JSON e, se disponibile, su MongoDB

### Tema
La topbar include un pulsante **☀ CHIARO / 🌙 SCURO** per passare tra il tema scuro (default, ispirato a GitHub/Strava) e il tema chiaro. La preferenza non viene salvata tra le sessioni.

### Export
Dal menu **ESPORTA** (richiede un'attività aperta):
- **PNG** — tutti e cinque i grafici in alta risoluzione (180 dpi)
- **PDF** — report 2 pagine: riepilogo testuale + splits + grafici
- **CSV** — splits chilometro per chilometro

---

## Architettura tecnica

```
strava_viewer/
├── main.py                  # Entry point — avvia StravaApp
├── config.py                # Costanti: colori, URL Strava, parametri MongoDB
├── models.py                # Classe ActivityData — parsing JSON Strava, proprietà calcolate
├── storage.py               # JSONStorage e MongoStorage — salvataggio/lettura attività
├── storage_manager.py       # Facade: unifica JSON e MongoDB, gestisce connessione Docker
├── downloader.py            # OAuth2 Strava, download lista e dettaglio attività
├── docker-compose.yml       # MongoDB 7 su porta 27017 (avvio automatico)
└── ui/
    ├── __init__.py
    ├── app.py               # StravaApp (tk.Tk) — finestra principale, menu, notebook
    ├── widgets.py           # Widget riutilizzabili: StatCard, make_scrollable, embed_mpl…
    ├── downloader_ui.py     # Finestra modale download da Strava
    ├── export_pdf.py        # Generazione PDF 2 pagine con matplotlib PdfPages
    ├── tab_dashboard.py     # Tab Dashboard
    ├── tab_charts.py        # Tab Grafici + _build_export_fig() per PNG/PDF
    ├── tab_hr.py            # Tab Zone HR
    ├── tab_map.py           # Tab Mappa (apre browser esterno)
    ├── tab_splits.py        # Tab Splits
    ├── tab_best.py          # Tab Best Efforts
    ├── tab_compare.py       # Tab Confronto
    ├── tab_library.py       # Tab Libreria con paginazione
    ├── tab_stats.py         # Tab Statistiche globali
    └── tab_raw.py           # Tab JSON grezzo
```

### Storage
L'applicazione supporta due backend di storage in parallelo, gestiti da `StorageManager`:

| Backend | Formato | Posizione default | Quando si usa |
|---|---|---|---|
| **JSONStorage** | Un file `.json` per corsa | `./activities/` | Sempre disponibile, offline |
| **MongoStorage** | Collezione MongoDB | `localhost:27017` | Se MongoDB è raggiungibile |

`StorageManager` tenta la connessione a MongoDB all'avvio in un thread in background. Se disponibile, la Libreria e le Statistiche leggono da MongoDB; altrimenti da file JSON.

### Connessione MongoDB
`StorageManager.connect_mongo(auto_start=True)` tenta:
1. Connessione diretta a `localhost:27017`
2. Se fallisce, esegue `docker compose up -d` e riprova per 5 volte (intervallo 3s)

Lo stato della connessione è visibile nella topbar (● verde = connesso, ○ grigio = offline). Cliccando sull'indicatore si può attivare/disattivare manualmente.

### OAuth2 Strava
Il flusso OAuth2 in `downloader.py`:
1. Apre il browser sul form di autorizzazione Strava
2. Avvia un server HTTP locale su `localhost:8765` in un thread daemon
3. Cattura il codice di autorizzazione dal redirect
4. Scambia il codice con access token + refresh token
5. Salva il token in `.strava_token.json` (rinnovo automatico alla scadenza)

---

## Requisiti

- **Python 3.10+**
- **Docker Desktop** (opzionale, solo per MongoDB)

### Dipendenze Python

```
pip install requests folium matplotlib pymongo tkinterweb
```

| Libreria | Uso |
|---|---|
| `requests` | Chiamate API Strava |
| `folium` | Generazione mappa HTML |
| `matplotlib` | Grafici, export PNG/PDF |
| `pymongo` | Connessione MongoDB |
| `tkinter` | Interfaccia grafica (incluso in Python standard) |

---

## Avvio

```bash
python main.py
```

---

## Configurazione

Tutti i parametri si trovano in `config.py`:

```python
# Directory salvataggio file JSON
JSON_STORAGE_DIR = "activities"

# MongoDB
MONGO_URI        = "mongodb://localhost:27017"
MONGO_DB         = "strava"
MONGO_COLLECTION = "activities"

# Token OAuth Strava salvato in
STRAVA_TOKEN_FILE = ".strava_token.json"

# Numero massimo attività nel confronto
MAX_COMPARE = 5
```

### Configurare l'app Strava (primo accesso)

1. Vai su [https://www.strava.com/settings/api](https://www.strava.com/settings/api)
2. Crea una nuova applicazione
3. Imposta **Authorization Callback Domain** su `localhost`
4. Copia **Client ID** e **Client Secret**
5. Nell'app clicca **SCARICA DA STRAVA**, inserisci le credenziali e clicca **▶ AVVIA DOWNLOAD**
6. Il browser si aprirà per l'autorizzazione — accedi e autorizza
7. Il download partirà automaticamente
8. Potrebbe essere necessario far ripartire la procedura nei giorni successivi a causa dei rate limit imposti da Strava

> **Nota:** Per scaricare le polyline GPS (necessarie per la mappa) l'app richiede lo scope `activity:read_all`. Strava lo chiede automaticamente durante l'autorizzazione.

### MongoDB con Docker

Se Docker Desktop è installato, MongoDB parte automaticamente al primo avvio dell'app. In alternativa puoi avviarlo manualmente:

```bash
docker compose up -d
```

Per fermarlo:

```bash
docker compose down
```

I dati MongoDB vengono salvati in un volume Docker persistente e sopravvivono ai riavvii.

---

## Note operative

- La prima volta che si scaricano le corse viene aperto il browser per l'autenticazione Strava; nelle sessioni successive il token viene rinnovato automaticamente senza aprire il browser
- Il download è incrementale: le corse già presenti nel database vengono saltate automaticamente
- La mappa GPS richiede una connessione internet per caricare i tile nel browser (CartoDB, OpenStreetMap, Esri Satellite)
- L'export PDF richiede `matplotlib` installato

## Utilizzo IA

- L'applicazione è stata interamente realizzata utilizzando l'IA Claude Code con il modello Sonnet 4.6
