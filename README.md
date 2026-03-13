# ⬡ Strava Viewer 3.0

Applicazione desktop per analizzare, visualizzare e confrontare le attività di corsa scaricate da Strava. Interfaccia grafica nativa (tkinter), tema chiaro/scuro, supporto MongoDB e archiviazione locale JSON.

---

> Se questo progetto ti è utile e ti va di offrire un caffè virtuale allo sviluppatore, puoi farlo qui → [☕ PayPal](https://paypal.me/TeoVr81). Nessuna pressione — ogni km conta, donazione o no.

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

### Calendario
Vista mensile di tutte le corse con navigazione mese per mese:
- Ogni cella mostra distanza e passo della corsa del giorno (colorata di arancione se presente)
- Giorni con più corse mostrano un contatore aggiuntivo
- Bottoni ◀ ▶ per navigare tra i mesi, "Oggi" per tornare al mese corrente
- Click su una cella apre l'attività nel tab Dashboard
- Il totale km e numero di corse del mese è visualizzato nell'intestazione

### Statistiche
Statistiche aggregate su **tutte** le corse nel database (ignora filtri e paginazione):
- **Obiettivo annuale** — imposta un target km per l'anno corrente con barra di avanzamento; il valore viene salvato in `settings.json` e ricordato tra le sessioni
- Totali: corse, km, ore, dislivello, passo medio, HR media, calorie, km/settimana
- **Tabella per mese** — ultimi 12 mesi con km, corse, tempo, passo medio, dislivello; grafico a barre km per mese
- Tabella per anno con km, corse, tempo, passo medio, dislivello; grafico km per anno e corse per anno
- Distribuzione distanze (torta)
- **Carico di allenamento** — grafico ATL/CTL/TSB (Banister TRIMP) degli ultimi 12 mesi:
  - *CTL (Fitness)* — media ponderata esponenziale a 42 giorni
  - *ATL (Fatica)* — media ponderata esponenziale a 7 giorni
  - *TSB (Forma)* — CTL − ATL (positivo = riposato, negativo = affaticato)
- **Record personali** — tabella con il miglior tempo personale per le distanze canoniche (1 km, 5 km, 10 km, Mezza Maratona, Maratona), con nome attività e data in cui è stato realizzato
- **Analisi pendenza (Grade Analysis)** — grafico a barre del passo mediano suddiviso per 6 fasce di gradiente (da discesa ripida <−8% a salita >8%), calcolato dai split di 1 km registrati da Strava; filtri "Ultimi giorni" e "Solo gare"; i dati di questo grafico alimentano la correzione dislivello personalizzata della Previsione Prestazioni; pulsante ℹ con guida per fascia e suggerimenti di allenamento
- **Curva di performance** — plot log-log distanza vs tempo sui best effort (da 400m alla maratona) con fit della legge di potenza `t = A × d^b`; i tempi usati sono il `moving_time` (escluse le pause); filtri "Ultimi giorni" e "Solo gare"; l'esponente `b` rivela il profilo atletico (velocista vs fondista, confronto con b=1.06 di Riegel); pulsante ℹ con teoria e guida interpretativa
- **Previsione prestazioni (Monte Carlo)** — stima del tempo su qualsiasi distanza con simulazione di 5000 scenari; parametri configurabili: distanza target (standard o personalizzata in km), dislivello positivo del percorso, finestra temporale dello storico (ultimi N giorni), lunghezza minima e massima delle corse da cui reperire i best effort (km min/max), filtro solo gare; la correzione dislivello è personalizzata: viene calcolata tramite regressione lineare sui tuoi split reali (sec/km per 1% di pendenza), con fallback al modello Minetti se i dati sono insufficienti; il risultato è un istogramma con i percentili P10/P25/P50/P75/P90 e un pannello diagnostico con i dati usati nel fit, il coefficiente b e il tempo base grezzo; pulsante ℹ con guida completa su parametri, calcolo e interpretazione dei risultati

### Database
Dal menu **DATABASE** nella topbar:
- **Esporta ZIP** — esporta tutte le attività del database in un archivio `.zip` (file JSON per ogni corsa); utile come backup o per spostare il database su un'altra macchina
- **Importa ZIP** — importa un archivio `.zip` precedentemente esportato; le attività già presenti vengono saltate (deduplicazione per Strava ID); le nuove vengono salvate su JSON e, se disponibile, su MongoDB
- **Heatmap corse** — genera una mappa interattiva nel browser con tutte le polyline GPS sovrapposte; sfondo scuro CartoDB, ogni tracciato in arancione semitrasparente; tooltip con nome e data al passaggio del mouse

### Tema
La topbar include un pulsante **☀ CHIARO / 🌙 SCURO** per passare tra il tema scuro (default, ispirato a GitHub/Strava) e il tema chiaro. La preferenza non viene salvata tra le sessioni.

### Export
Dal menu **ESPORTA**:
- **PNG** — tutti e cinque i grafici in alta risoluzione (180 dpi) *(richiede attività aperta)*
- **PDF** — report 2 pagine: riepilogo testuale + splits + grafici *(richiede attività aperta)*
- **CSV Splits** — splits chilometro per chilometro *(richiede attività aperta)*
- **GPX** — esporta il tracciato GPS in formato GPX standard, compatibile con Garmin, Komoot, ecc. *(richiede attività aperta con dati GPS)*
- **CSV Statistiche** — esporta le statistiche mensili (km, corse, tempo, passo, dislivello) in CSV per analisi esterne (Excel, ecc.)

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
    ├── tab_calendar.py      # Tab Calendario mensile
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
pip install requests folium matplotlib numpy pymongo tkinterweb
```

| Libreria | Uso |
|---|---|
| `requests` | Chiamate API Strava |
| `folium` | Generazione mappa HTML |
| `matplotlib` | Grafici, export PNG/PDF |
| `numpy` | Fit legge di potenza e simulazione Monte Carlo (curva performance + previsione gara) |
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
- La heatmap richiede una connessione internet per caricare i tile CartoDB nel browser

### File non tracciati da git

| File | Contenuto |
|---|---|
| `.strava_token.json` | Token OAuth Strava (access + refresh token) |
| `settings.json` | Preferenze utente locali (es. obiettivo km annuale) |
| `strava_activities/` | File JSON delle attività scaricate |

## Utilizzo IA

- L'applicazione è stata interamente realizzata utilizzando l'IA Claude Code con il modello Sonnet 4.6
