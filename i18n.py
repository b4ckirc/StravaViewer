# ── i18n.py ───────────────────────────────────────────────────────────────────
"""
Internationalisation support for Strava Viewer.

Usage:
    from i18n import t, set_language, get_language

    t("key")              → translated string for active language
    set_language("de")    → switch language
    get_language()        → "it" | "en" | "de" | "fr" | "es"

Fallback chain: active language → Italian → key itself.
"""

_active_lang: str = "it"

SUPPORTED_LANGUAGES = {
    "it": "🇮🇹 Italiano",
    "en": "🇬🇧 English",
    "de": "🇩🇪 Deutsch",
    "fr": "🇫🇷 Français",
    "es": "🇪🇸 Español",
}

_TRANSLATIONS: dict[str, dict[str, str]] = {

    # ── Tab names ─────────────────────────────────────────────────────────────
    "tab_dashboard":  {"it": "Dashboard",  "en": "Dashboard",  "de": "Dashboard",  "fr": "Tableau de bord", "es": "Panel"},
    "tab_charts":     {"it": "Grafici",    "en": "Charts",     "de": "Diagramme",  "fr": "Graphiques",      "es": "Gráficos"},
    "tab_hr":         {"it": "Zone HR",    "en": "HR Zones",   "de": "HF-Zonen",   "fr": "Zones FC",        "es": "Zonas FC"},
    "tab_map":        {"it": "Mappa",      "en": "Map",        "de": "Karte",       "fr": "Carte",           "es": "Mapa"},
    "tab_splits":     {"it": "Splits",     "en": "Splits",     "de": "Splits",      "fr": "Splits",          "es": "Parciales"},
    "tab_best":       {"it": "Best Efforts","en": "Best Efforts","de": "Bestleistungen","fr": "Meilleures perf.","es": "Mejores marcas"},
    "tab_compare":    {"it": "Confronto",  "en": "Compare",    "de": "Vergleich",   "fr": "Comparaison",     "es": "Comparar"},
    "tab_raw":        {"it": "Raw JSON",   "en": "Raw JSON",   "de": "Raw JSON",    "fr": "JSON brut",       "es": "JSON crudo"},
    "tab_library":    {"it": "Libreria",   "en": "Library",    "de": "Bibliothek",  "fr": "Bibliothèque",    "es": "Biblioteca"},
    "tab_calendar":   {"it": "Calendario", "en": "Calendar",   "de": "Kalender",    "fr": "Calendrier",      "es": "Calendario"},
    "tab_stats":      {"it": "Statistiche","en": "Statistics", "de": "Statistiken", "fr": "Statistiques",    "es": "Estadísticas"},

    # ── Sidebar section headers ────────────────────────────────────────────────
    "sidebar_analysis": {"it": "Analisi",  "en": "Analysis",   "de": "Analyse",     "fr": "Analyse",         "es": "Análisis"},
    "sidebar_database": {"it": "Database", "en": "Database",   "de": "Datenbank",   "fr": "Base de données", "es": "Base de datos"},

    # ── Topbar buttons ────────────────────────────────────────────────────────
    "btn_open_file":      {"it": "📂  Apri File",          "en": "📂  Open File",        "de": "📂  Datei öffnen",    "fr": "📂  Ouvrir fichier",   "es": "📂  Abrir archivo"},
    "btn_download":       {"it": "⬇  Scarica da Strava",  "en": "⬇  Download from Strava","de": "⬇  Von Strava laden","fr": "⬇  Télécharger Strava","es": "⬇  Descargar Strava"},
    "btn_export":         {"it": "💾  Esporta",            "en": "💾  Export",            "de": "💾  Exportieren",     "fr": "💾  Exporter",         "es": "💾  Exportar"},
    "btn_database":       {"it": "📦  Database",           "en": "📦  Database",          "de": "📦  Datenbank",       "fr": "📦  Base de données",  "es": "📦  Base de datos"},
    "btn_theme_dark":     {"it": "🌙  Scuro",              "en": "🌙  Dark",              "de": "🌙  Dunkel",          "fr": "🌙  Sombre",           "es": "🌙  Oscuro"},
    "btn_theme_light":    {"it": "☀  Chiaro",             "en": "☀  Light",             "de": "☀  Hell",            "fr": "☀  Clair",            "es": "☀  Claro"},

    # ── Topbar tooltips ───────────────────────────────────────────────────────
    "tooltip_open_file":  {"it": "Apri un file JSON di attività Strava",        "en": "Open a Strava activity JSON file",        "de": "Strava-Aktivitäts-JSON-Datei öffnen",     "fr": "Ouvrir un fichier JSON d'activité Strava",    "es": "Abrir un archivo JSON de actividad Strava"},
    "tooltip_download":   {"it": "Autentica con Strava e scarica le tue attività","en": "Authenticate with Strava and download your activities","de": "Mit Strava authentifizieren und Aktivitäten herunterladen","fr": "S'authentifier sur Strava et télécharger vos activités","es": "Autenticarse en Strava y descargar actividades"},
    "tooltip_export":     {"it": "Esporta attività corrente in PNG, PDF, CSV o GPX","en": "Export current activity as PNG, PDF, CSV or GPX","de": "Aktuelle Aktivität als PNG, PDF, CSV oder GPX exportieren","fr": "Exporter l'activité en PNG, PDF, CSV ou GPX","es": "Exportar actividad como PNG, PDF, CSV o GPX"},
    "tooltip_database":   {"it": "Backup ZIP, import e heatmap del database",    "en": "ZIP backup, import and database heatmap",  "de": "ZIP-Backup, Import und Datenbank-Heatmap",  "fr": "Sauvegarde ZIP, import et heatmap de la base","es": "Copia ZIP, importar y mapa de calor de BD"},
    "tooltip_theme":      {"it": "Passa al tema scuro / chiaro",                 "en": "Switch between dark / light theme",        "de": "Zwischen dunklem / hellem Theme wechseln", "fr": "Basculer thème sombre / clair",               "es": "Cambiar tema oscuro / claro"},

    # ── MongoDB status ────────────────────────────────────────────────────────
    "mongo_connecting":   {"it": "MongoDB: connessione…",  "en": "MongoDB: connecting…",  "de": "MongoDB: Verbindung…",  "fr": "MongoDB: connexion…",   "es": "MongoDB: conectando…"},
    "mongo_online":       {"it": "● MongoDB",              "en": "● MongoDB",              "de": "● MongoDB",             "fr": "● MongoDB",              "es": "● MongoDB"},
    "mongo_offline":      {"it": "○ MongoDB offline",      "en": "○ MongoDB offline",      "de": "○ MongoDB offline",     "fr": "○ MongoDB hors ligne",   "es": "○ MongoDB sin conexión"},

    # ── Welcome screen ────────────────────────────────────────────────────────
    "welcome_text": {
        "it": "⬡\n\nBenvenuto in Strava Viewer\n\n• Apri un file JSON con «Apri File»\n• Scarica le corse da Strava con «Scarica da Strava»\n• Sfoglia la libreria nel tab «Libreria»",
        "en": "⬡\n\nWelcome to Strava Viewer\n\n• Open a JSON file with «Open File»\n• Download runs from Strava with «Download from Strava»\n• Browse the library in the «Library» tab",
        "de": "⬡\n\nWillkommen bei Strava Viewer\n\n• JSON-Datei öffnen mit «Datei öffnen»\n• Aktivitäten von Strava laden mit «Von Strava laden»\n• Bibliothek durchsuchen im Tab «Bibliothek»",
        "fr": "⬡\n\nBienvenue dans Strava Viewer\n\n• Ouvrez un fichier JSON avec «Ouvrir fichier»\n• Téléchargez vos sorties depuis Strava avec «Télécharger Strava»\n• Parcourez la bibliothèque dans l'onglet «Bibliothèque»",
        "es": "⬡\n\nBienvenido a Strava Viewer\n\n• Abre un archivo JSON con «Abrir archivo»\n• Descarga actividades de Strava con «Descargar Strava»\n• Explora la biblioteca en la pestaña «Biblioteca»",
    },

    # ── Export menu ───────────────────────────────────────────────────────────
    "export_choose_format":  {"it": "SCEGLI FORMATO",           "en": "CHOOSE FORMAT",          "de": "FORMAT WÄHLEN",          "fr": "CHOISIR FORMAT",         "es": "ELEGIR FORMATO"},
    "export_current":        {"it": "— attività corrente —",    "en": "— current activity —",   "de": "— aktuelle Aktivität —", "fr": "— activité courante —",  "es": "— actividad actual —"},
    "export_database":       {"it": "— database completo —",    "en": "— full database —",      "de": "— vollständige DB —",    "fr": "— base de données —",    "es": "— base de datos completa —"},
    "export_png":            {"it": "📊  PNG — Grafici",        "en": "📊  PNG — Charts",       "de": "📊  PNG — Diagramme",    "fr": "📊  PNG — Graphiques",   "es": "📊  PNG — Gráficos"},
    "export_pdf":            {"it": "📄  PDF — Report",         "en": "📄  PDF — Report",       "de": "📄  PDF — Bericht",      "fr": "📄  PDF — Rapport",      "es": "📄  PDF — Informe"},
    "export_csv_splits":     {"it": "📋  CSV — Splits",         "en": "📋  CSV — Splits",       "de": "📋  CSV — Splits",       "fr": "📋  CSV — Splits",       "es": "📋  CSV — Parciales"},
    "export_gpx":            {"it": "📍  GPX — Tracciato",      "en": "📍  GPX — Route",        "de": "📍  GPX — Strecke",      "fr": "📍  GPX — Tracé",        "es": "📍  GPX — Ruta"},
    "export_csv_stats":      {"it": "📈  CSV — Statistiche",    "en": "📈  CSV — Statistics",   "de": "📈  CSV — Statistiken",  "fr": "📈  CSV — Statistiques", "es": "📈  CSV — Estadísticas"},
    "btn_cancel":            {"it": "✕  Annulla",               "en": "✕  Cancel",              "de": "✕  Abbrechen",           "fr": "✕  Annuler",             "es": "✕  Cancelar"},
    "msg_open_activity_first":{"it": "Apri prima un'attività.", "en": "Open an activity first.","de": "Zuerst eine Aktivität öffnen.","fr": "Ouvrez d'abord une activité.","es": "Abre primero una actividad."},

    # ── Database menu ─────────────────────────────────────────────────────────
    "db_manage":             {"it": "GESTIONE DATABASE",        "en": "DATABASE MANAGEMENT",    "de": "DATENBANKVERWALTUNG",    "fr": "GESTION BASE DE DONNÉES","es": "GESTIÓN BASE DE DATOS"},
    "db_export_zip":         {"it": "📦  Esporta tutto (ZIP)",  "en": "📦  Export all (ZIP)",   "de": "📦  Alles exportieren (ZIP)","fr": "📦  Exporter tout (ZIP)","es": "📦  Exportar todo (ZIP)"},
    "db_import_zip":         {"it": "📥  Importa da ZIP",       "en": "📥  Import from ZIP",    "de": "📥  Von ZIP importieren", "fr": "📥  Importer depuis ZIP","es": "📥  Importar desde ZIP"},
    "db_heatmap":            {"it": "🗺  Heatmap corse",        "en": "🗺  Runs heatmap",       "de": "🗺  Lauf-Heatmap",       "fr": "🗺  Carte de chaleur",   "es": "🗺  Mapa de calor"},

    # ── Messages ──────────────────────────────────────────────────────────────
    "msg_language_restart":  {"it": "La lingua verrà applicata al prossimo avvio.", "en": "The language will be applied on next startup.", "de": "Die Sprache wird beim nächsten Start angewendet.", "fr": "La langue sera appliquée au prochain démarrage.", "es": "El idioma se aplicará en el próximo inicio."},
    "msg_language_changed":  {"it": "Lingua aggiornata",        "en": "Language updated",       "de": "Sprache aktualisiert",   "fr": "Langue mise à jour",     "es": "Idioma actualizado"},
    "msg_no_data":           {"it": "Nessun dato disponibile.", "en": "No data available.",     "de": "Keine Daten verfügbar.", "fr": "Aucune donnée disponible.","es": "No hay datos disponibles."},
    "msg_no_activity":       {"it": "Impossibile caricare l'attività.", "en": "Unable to load activity.", "de": "Aktivität kann nicht geladen werden.", "fr": "Impossible de charger l'activité.", "es": "No se puede cargar la actividad."},
    "msg_select_activity":   {"it": "Seleziona almeno un'attività.", "en": "Select at least one activity.", "de": "Mindestens eine Aktivität auswählen.", "fr": "Sélectionnez au moins une activité.", "es": "Selecciona al menos una actividad."},
    "msg_add_two_for_compare":{"it": "Aggiungi almeno 2 attività per il confronto.\n\nPrima apri un'attività principale, poi aggiungi altre dal tab Libreria col pulsante ➕.", "en": "Add at least 2 activities to compare.\n\nFirst open a main activity, then add others from the Library tab using the ➕ button.", "de": "Füge mindestens 2 Aktivitäten zum Vergleich hinzu.\n\nÖffne zuerst eine Hauptaktivität und füge weitere über den ➕ Knopf in der Bibliothek hinzu.", "fr": "Ajoutez au moins 2 activités pour la comparaison.\n\nOuvrez d'abord une activité principale, puis ajoutez-en d'autres depuis la bibliothèque avec le bouton ➕.", "es": "Añade al menos 2 actividades para comparar.\n\nAbre primero una actividad principal, luego añade otras desde la biblioteca con el botón ➕."},
    "msg_max_compare":       {"it": "Massimo {n} attività.",   "en": "Maximum {n} activities.", "de": "Maximal {n} Aktivitäten.","fr": "Maximum {n} activités.",  "es": "Máximo {n} actividades."},
    "msg_limit":             {"it": "Limite",                  "en": "Limit",                  "de": "Limit",                  "fr": "Limite",                 "es": "Límite"},
    "msg_error":             {"it": "Errore",                  "en": "Error",                  "de": "Fehler",                 "fr": "Erreur",                 "es": "Error"},
    "msg_info":              {"it": "Info",                    "en": "Info",                   "de": "Info",                   "fr": "Info",                   "es": "Info"},
    "msg_read_error":        {"it": "Errore lettura",          "en": "Read error",             "de": "Lesefehler",             "fr": "Erreur de lecture",      "es": "Error de lectura"},
    "msg_export_saved":      {"it": "Export",                  "en": "Export",                 "de": "Export",                 "fr": "Export",                 "es": "Exportar"},
    "msg_export_error":      {"it": "Errore export",           "en": "Export error",           "de": "Exportfehler",           "fr": "Erreur d'export",        "es": "Error al exportar"},
    "msg_no_gps":            {"it": "Nessun dato GPS disponibile per questa attività.", "en": "No GPS data available for this activity.", "de": "Keine GPS-Daten für diese Aktivität.", "fr": "Aucune donnée GPS pour cette activité.", "es": "Sin datos GPS para esta actividad."},
    "msg_import_done":       {"it": "Importazione completata:", "en": "Import completed:",     "de": "Import abgeschlossen:",  "fr": "Importation terminée :",  "es": "Importación completada:"},
    "msg_backup_done":       {"it": "Backup completato.",      "en": "Backup completed.",      "de": "Backup abgeschlossen.",  "fr": "Sauvegarde terminée.",    "es": "Copia de seguridad completada."},
    "msg_runs_exported":     {"it": "corse esportate in:",     "en": "runs exported to:",      "de": "Läufe exportiert nach:", "fr": "sorties exportées vers :", "es": "carreras exportadas en:"},
    "msg_imported":          {"it": "corse importate",         "en": "runs imported",          "de": "Läufe importiert",       "fr": "sorties importées",       "es": "carreras importadas"},
    "msg_already_present":   {"it": "già presenti (saltate)", "en": "already present (skipped)","de": "bereits vorhanden (übersprungen)","fr": "déjà présentes (ignorées)","es": "ya presentes (omitidas)"},
    "msg_errors":            {"it": "errori",                  "en": "errors",                 "de": "Fehler",                 "fr": "erreurs",                "es": "errores"},
    "msg_heatmap_loading":   {"it": "Caricamento polyline in corso…", "en": "Loading polylines…", "de": "Polylinien werden geladen…", "fr": "Chargement des tracés…", "es": "Cargando rutas…"},
    "msg_heatmap_no_gps":    {"it": "Nessun tracciato GPS trovato nel database.", "en": "No GPS track found in the database.", "de": "Kein GPS-Track in der Datenbank gefunden.", "fr": "Aucun tracé GPS trouvé dans la base de données.", "es": "No se encontraron rutas GPS en la base de datos."},
    "msg_folium_missing":    {"it": "Libreria 'folium' non installata.\nEsegui: pip install folium", "en": "Library 'folium' not installed.\nRun: pip install folium", "de": "Bibliothek 'folium' nicht installiert.\nAusführen: pip install folium", "fr": "Bibliothèque 'folium' non installée.\nExécuter : pip install folium", "es": "Librería 'folium' no instalada.\nEjecuta: pip install folium"},
    "msg_select_file":       {"it": "Seleziona attività Strava (JSON)", "en": "Select Strava activity (JSON)", "de": "Strava-Aktivität auswählen (JSON)", "fr": "Sélectionner une activité Strava (JSON)", "es": "Seleccionar actividad Strava (JSON)"},
    "msg_select_backup":     {"it": "Seleziona backup ZIP",    "en": "Select ZIP backup",      "de": "ZIP-Backup auswählen",   "fr": "Sélectionner sauvegarde ZIP","es": "Seleccionar copia ZIP"},
    "msg_png_saved":         {"it": "PNG salvato:",            "en": "PNG saved:",             "de": "PNG gespeichert:",       "fr": "PNG sauvegardé :",        "es": "PNG guardado:"},
    "msg_pdf_saved":         {"it": "PDF salvato:",            "en": "PDF saved:",             "de": "PDF gespeichert:",       "fr": "PDF sauvegardé :",        "es": "PDF guardado:"},
    "msg_csv_saved":         {"it": "CSV salvato:",            "en": "CSV saved:",             "de": "CSV gespeichert:",       "fr": "CSV sauvegardé :",        "es": "CSV guardado:"},
    "msg_gpx_saved":         {"it": "GPX salvato:",            "en": "GPX saved:",             "de": "GPX gespeichert:",       "fr": "GPX sauvegardé :",        "es": "GPX guardado:"},
    "msg_stats_exported":    {"it": "Statistiche esportate:",  "en": "Statistics exported:",   "de": "Statistiken exportiert:","fr": "Statistiques exportées :", "es": "Estadísticas exportadas:"},
    "msg_gpx_error":         {"it": "Errore GPX",             "en": "GPX error",              "de": "GPX-Fehler",             "fr": "Erreur GPX",              "es": "Error GPX"},
    "msg_csv_error":         {"it": "Errore CSV",             "en": "CSV error",              "de": "CSV-Fehler",             "fr": "Erreur CSV",              "es": "Error CSV"},
    "msg_delete_confirm":    {"it": "Eliminare '{name}'?",    "en": "Delete '{name}'?",       "de": "'{name}' löschen?",      "fr": "Supprimer '{name}' ?",    "es": "¿Eliminar '{name}'?"},
    "msg_delete":            {"it": "Elimina",                "en": "Delete",                 "de": "Löschen",                "fr": "Supprimer",               "es": "Eliminar"},

    # ── Language selector ─────────────────────────────────────────────────────
    "language_label":        {"it": "🌐 Lingua:",             "en": "🌐 Language:",           "de": "🌐 Sprache:",            "fr": "🌐 Langue :",             "es": "🌐 Idioma:"},

    # ── Filter bar (tab_library) ───────────────────────────────────────────────
    "filter_label":          {"it": "FILTRI:",                "en": "FILTERS:",               "de": "FILTER:",                "fr": "FILTRES :",               "es": "FILTROS:"},
    "filter_name":           {"it": "Nome:",                  "en": "Name:",                  "de": "Name:",                  "fr": "Nom :",                   "es": "Nombre:"},
    "filter_dist_km":        {"it": "Dist km:",               "en": "Dist km:",               "de": "Dist km:",               "fr": "Dist km :",               "es": "Dist km:"},
    "filter_elev_m":         {"it": "Disl m:",                "en": "Elev m:",                "de": "Höhenm.:",               "fr": "Dénivelé m :",            "es": "Desnivel m:"},
    "filter_date_from":      {"it": "Dal:",                   "en": "From:",                  "de": "Von:",                   "fr": "Du :",                    "es": "Desde:"},
    "filter_date_to":        {"it": "Al:",                    "en": "To:",                    "de": "Bis:",                   "fr": "Au :",                    "es": "Hasta:"},
    "filter_races_only":     {"it": "Solo gare",              "en": "Races only",             "de": "Nur Rennen",             "fr": "Courses seulement",       "es": "Solo carreras"},
    "btn_search":            {"it": "🔍",                     "en": "🔍",                     "de": "🔍",                     "fr": "🔍",                      "es": "🔍"},
    "btn_calculate":         {"it": "▶  CALCOLA",             "en": "▶  CALCULATE",           "de": "▶  BERECHNEN",           "fr": "▶  CALCULER",             "es": "▶  CALCULAR"},

    # ── Library columns ───────────────────────────────────────────────────────
    "col_date":              {"it": "DATA",     "en": "DATE",     "de": "DATUM",    "fr": "DATE",     "es": "FECHA"},
    "col_name":              {"it": "NOME",     "en": "NAME",     "de": "NAME",     "fr": "NOM",      "es": "NOMBRE"},
    "col_dist":              {"it": "DIST.",    "en": "DIST.",    "de": "DIST.",    "fr": "DIST.",     "es": "DIST."},
    "col_time":              {"it": "TEMPO",    "en": "TIME",     "de": "ZEIT",     "fr": "TEMPS",    "es": "TIEMPO"},
    "col_pace":              {"it": "PASSO",    "en": "PACE",     "de": "TEMPO",    "fr": "ALLURE",   "es": "RITMO"},
    "col_hr":                {"it": "HR",       "en": "HR",       "de": "HF",       "fr": "FC",       "es": "FC"},
    "col_elev":              {"it": "↑ELEV",    "en": "↑ELEV",    "de": "↑HÖHE",    "fr": "↑DÉNI.",   "es": "↑DESNIV."},
    "col_actions":           {"it": "AZIONI",   "en": "ACTIONS",  "de": "AKTIONEN", "fr": "ACTIONS",  "es": "ACCIONES"},

    # ── Library row actions ────────────────────────────────────────────────────
    "btn_open":              {"it": "📂 Apri",       "en": "📂 Open",       "de": "📂 Öffnen",      "fr": "📂 Ouvrir",      "es": "📂 Abrir"},
    "btn_compare_add":       {"it": "➕ Confronto",  "en": "➕ Compare",    "de": "➕ Vergleich",   "fr": "➕ Comparer",    "es": "➕ Comparar"},
    "btn_open_strava":       {"it": "🟠 Strava",     "en": "🟠 Strava",     "de": "🟠 Strava",      "fr": "🟠 Strava",      "es": "🟠 Strava"},
    "btn_delete":            {"it": "🗑",            "en": "🗑",            "de": "🗑",             "fr": "🗑",             "es": "🗑"},

    # ── Compare bar ───────────────────────────────────────────────────────────
    "compare_none":          {"it": "Confronto: nessuna selezione",  "en": "Compare: no selection",  "de": "Vergleich: keine Auswahl", "fr": "Comparaison : aucune sélection", "es": "Comparar: sin selección"},
    "compare_count":         {"it": "Confronto [{n}/4]:",            "en": "Compare [{n}/4]:",        "de": "Vergleich [{n}/4]:",       "fr": "Comparaison [{n}/4] :",          "es": "Comparar [{n}/4]:"},
    "btn_clear_compare":     {"it": "🗑 Svuota confronto",          "en": "🗑 Clear compare",        "de": "🗑 Vergleich leeren",      "fr": "🗑 Vider comparaison",           "es": "🗑 Limpiar comparación"},
    "btn_run_compare":       {"it": "▶ Avvia confronto",            "en": "▶ Start compare",         "de": "▶ Vergleich starten",      "fr": "▶ Lancer comparaison",           "es": "▶ Iniciar comparación"},
    "compare_limit":         {"it": "Puoi confrontare al massimo {n} attività.", "en": "You can compare at most {n} activities.", "de": "Du kannst maximal {n} Aktivitäten vergleichen.", "fr": "Vous pouvez comparer au maximum {n} activités.", "es": "Puedes comparar como máximo {n} actividades."},

    # ── Pagination ────────────────────────────────────────────────────────────
    "page_next":             {"it": "▶  Pag. successiva",    "en": "▶  Next page",     "de": "▶  Nächste Seite",   "fr": "▶  Page suivante",   "es": "▶  Página siguiente"},
    "page_prev":             {"it": "◀  Pag. precedente",   "en": "◀  Previous page", "de": "◀  Vorherige Seite", "fr": "◀  Page précédente", "es": "◀  Página anterior"},
    "page_info":             {"it": "Pagina {cur} / {tot}  (righe {from}–{to} di {all})", "en": "Page {cur} / {tot}  (rows {from}–{to} of {all})", "de": "Seite {cur} / {tot}  (Zeilen {from}–{to} von {all})", "fr": "Page {cur} / {tot}  (lignes {from}–{to} sur {all})", "es": "Página {cur} / {tot}  (filas {from}–{to} de {all})"},
    "unit_runs":             {"it": "corse",  "en": "runs",   "de": "Läufe",  "fr": "sorties", "es": "carreras"},
    "runs_total":            {"it": "{n} corse totali",      "en": "{n} runs total",   "de": "{n} Läufe gesamt",   "fr": "{n} sorties au total","es": "{n} carreras en total"},
    "page_label":            {"it": "Pag. {cur} / {tot}",   "en": "Page {cur} / {tot}","de": "Seite {cur} / {tot}","fr": "Page {cur} / {tot}", "es": "Pág. {cur} / {tot}"},

    # ── Library empty state ────────────────────────────────────────────────────
    "library_empty":         {"it": "Nessuna corsa trovata.\n\nScarica le attività da Strava oppure apri un file JSON.", "en": "No runs found.\n\nDownload activities from Strava or open a JSON file.", "de": "Keine Läufe gefunden.\n\nLade Aktivitäten von Strava oder öffne eine JSON-Datei.", "fr": "Aucune sortie trouvée.\n\nTéléchargez vos activités depuis Strava ou ouvrez un fichier JSON.", "es": "No se encontraron carreras.\n\nDescarga actividades de Strava o abre un archivo JSON."},

    # ── Dashboard section headers ──────────────────────────────────────────────
    "section_main_stats":    {"it": "STATISTICHE PRINCIPALI",  "en": "MAIN STATISTICS",      "de": "HAUPTSTATISTIKEN",       "fr": "STATISTIQUES PRINCIPALES","es": "ESTADÍSTICAS PRINCIPALES"},
    "section_heart_rate":    {"it": "FREQUENZA CARDIACA",      "en": "HEART RATE",            "de": "HERZFREQUENZ",           "fr": "FRÉQUENCE CARDIAQUE",     "es": "FRECUENCIA CARDÍACA"},
    "section_extra_details": {"it": "DETTAGLI AGGIUNTIVI",     "en": "ADDITIONAL DETAILS",    "de": "WEITERE DETAILS",        "fr": "DÉTAILS SUPPLÉMENTAIRES", "es": "DETALLES ADICIONALES"},
    "section_perf_indices":  {"it": "INDICI DI PERFORMANCE",   "en": "PERFORMANCE INDICES",   "de": "LEISTUNGSINDIZES",       "fr": "INDICES DE PERFORMANCE",  "es": "ÍNDICES DE RENDIMIENTO"},

    # ── Dashboard stat labels ─────────────────────────────────────────────────
    "stat_distance":         {"it": "Distanza",        "en": "Distance",       "de": "Distanz",        "fr": "Distance",       "es": "Distancia"},
    "stat_moving_time":      {"it": "Tempo attivo",    "en": "Moving time",    "de": "Bewegungszeit",  "fr": "Temps actif",    "es": "Tiempo activo"},
    "stat_avg_pace":         {"it": "Passo medio",     "en": "Avg pace",       "de": "Durchschnittstempo","fr": "Allure moy.", "es": "Ritmo medio"},
    "stat_elev_gain":        {"it": "Dislivello +",    "en": "Elevation gain", "de": "Höhengewinn",    "fr": "Dénivelé +",     "es": "Desnivel +"},
    "stat_total_time":       {"it": "Tempo totale",    "en": "Total time",     "de": "Gesamtzeit",     "fr": "Temps total",    "es": "Tiempo total"},
    "stat_best_pace":        {"it": "Passo migliore",  "en": "Best pace",      "de": "Besttempo",      "fr": "Meilleure allure","es": "Mejor ritmo"},
    "stat_avg_hr":           {"it": "HR Media",        "en": "Avg HR",         "de": "Ø Herzfrequenz", "fr": "FC moy.",        "es": "FC media"},
    "stat_max_hr":           {"it": "HR Massima",      "en": "Max HR",         "de": "Max Herzfrequenz","fr": "FC max.",       "es": "FC máx."},
    "stat_cadence":          {"it": "Cadenza",         "en": "Cadence",        "de": "Kadenz",         "fr": "Cadence",        "es": "Cadencia"},
    "stat_calories":         {"it": "Calorie",         "en": "Calories",       "de": "Kalorien",       "fr": "Calories",       "es": "Calorías"},
    "stat_suffer_score":     {"it": "Suffer Score",    "en": "Suffer Score",   "de": "Belastungsscore","fr": "Score effort",   "es": "Índice esfuerzo"},
    "stat_achievements":     {"it": "Achievement",     "en": "Achievements",   "de": "Erfolge",        "fr": "Accomplissements","es": "Logros"},
    "stat_pr_count":         {"it": "Record pers.",    "en": "Personal records","de": "Persönl. Rekorde","fr": "Records perso.","es": "Récords pers."},
    "stat_power":            {"it": "Potenza",         "en": "Power",          "de": "Leistung",       "fr": "Puissance",      "es": "Potencia"},
    "stat_elev_high":        {"it": "Quota max",       "en": "Max elevation",  "de": "Höchste Höhe",   "fr": "Altitude max",   "es": "Altitud máx."},
    "stat_elev_low":         {"it": "Quota min",       "en": "Min elevation",  "de": "Niedrigste Höhe","fr": "Altitude min",   "es": "Altitud mín."},
    "stat_device":           {"it": "Dispositivo",     "en": "Device",         "de": "Gerät",          "fr": "Appareil",       "es": "Dispositivo"},
    "stat_gear":             {"it": "Gear",            "en": "Gear",           "de": "Ausrüstung",     "fr": "Équipement",     "es": "Equipamiento"},
    "stat_eff_index":        {"it": "Indice efficienza","en": "Efficiency index","de": "Effizienzindex","fr": "Indice d'efficacité","es": "Índice eficiencia"},
    "stat_vo2max":           {"it": "VO2max stimato",  "en": "Estimated VO2max","de": "Geschätztes VO2max","fr": "VO2max estimé","es": "VO2max estimado"},
    "stat_avg_speed":        {"it": "Velocità media",  "en": "Avg speed",      "de": "Durchschnittsgeschw.","fr": "Vitesse moy.","es": "Velocidad media"},
    "stat_stops":            {"it": "Soste totali",    "en": "Total stops",    "de": "Gesamtpausen",   "fr": "Pauses totales", "es": "Paradas totales"},
    "stat_open_strava":      {"it": "🟠 Apri su Strava","en": "🟠 Open on Strava","de": "🟠 Auf Strava öffnen","fr": "🟠 Voir sur Strava","es": "🟠 Abrir en Strava"},

    # ── Stats tab ─────────────────────────────────────────────────────────────
    "stats_global_title":    {"it": "STATISTICHE GLOBALI",       "en": "GLOBAL STATISTICS",     "de": "GLOBALE STATISTIKEN",    "fr": "STATISTIQUES GLOBALES",  "es": "ESTADÍSTICAS GLOBALES"},
    "section_overview":      {"it": "RIEPILOGO COMPLESSIVO",     "en": "OVERALL SUMMARY",       "de": "GESAMTÜBERSICHT",        "fr": "RÉSUMÉ GLOBAL",          "es": "RESUMEN GENERAL"},
    "section_details":       {"it": "DETTAGLI",                  "en": "DETAILS",               "de": "DETAILS",                "fr": "DÉTAILS",                "es": "DETALLES"},
    "stat_total_runs":       {"it": "Corse totali",              "en": "Total runs",            "de": "Läufe gesamt",           "fr": "Sorties totales",        "es": "Carreras totales"},
    "stat_total_km":         {"it": "Km totali",                 "en": "Total km",              "de": "Gesamt-km",              "fr": "Km totaux",              "es": "Km totales"},
    "stat_total_hours":      {"it": "Ore totali",                "en": "Total hours",           "de": "Gesamtstunden",          "fr": "Heures totales",         "es": "Horas totales"},
    "stat_total_elev":       {"it": "Dislivello tot.",           "en": "Total elev. gain",      "de": "Gesamter Aufstieg",      "fr": "Dénivelé total",         "es": "Desnivel total"},
    "stat_avg_pace_label":   {"it": "Passo medio",              "en": "Avg pace",              "de": "Ø Tempo",                "fr": "Allure moy.",            "es": "Ritmo medio"},
    "stat_hr_avg":           {"it": "HR media",                 "en": "Avg HR",                "de": "Ø Herzfrequenz",         "fr": "FC moy.",                "es": "FC media"},
    "stat_avg_dist":         {"it": "Dist. media",              "en": "Avg distance",          "de": "Ø Distanz",              "fr": "Distance moy.",          "es": "Distancia media"},
    "stat_longest_run":      {"it": "Corsa più lunga",          "en": "Longest run",           "de": "Längster Lauf",          "fr": "Sortie la plus longue",  "es": "Carrera más larga"},
    "stat_total_calories":   {"it": "Calorie totali",           "en": "Total calories",        "de": "Kalorien gesamt",        "fr": "Calories totales",       "es": "Calorías totales"},
    "stat_km_per_week":      {"it": "Media km/sett.",           "en": "Avg km/week",           "de": "Ø km/Woche",             "fr": "Km/sem. moy.",           "es": "Km/semana med."},

    # ── Stats by year ─────────────────────────────────────────────────────────
    "section_by_year":       {"it": "STATISTICHE PER ANNO",      "en": "STATISTICS BY YEAR",    "de": "STATISTIKEN NACH JAHR",  "fr": "STATISTIQUES PAR ANNÉE", "es": "ESTADÍSTICAS POR AÑO"},
    "col_year":              {"it": "ANNO",                       "en": "YEAR",                  "de": "JAHR",                   "fr": "ANNÉE",                  "es": "AÑO"},
    "col_runs":              {"it": "CORSE",                      "en": "RUNS",                  "de": "LÄUFE",                  "fr": "SORTIES",                "es": "CARRERAS"},
    "col_km_total":          {"it": "KM TOT.",                    "en": "TOTAL KM",              "de": "KM GESAMT",              "fr": "KM TOTAL",               "es": "KM TOTAL"},
    "col_time_total":        {"it": "TEMPO TOT.",                 "en": "TOTAL TIME",            "de": "GESAMTZEIT",             "fr": "TEMPS TOTAL",            "es": "TIEMPO TOTAL"},
    "col_avg_pace":          {"it": "PASSO MEDIO",                "en": "AVG PACE",              "de": "Ø TEMPO",                "fr": "ALLURE MOY.",            "es": "RITMO MEDIO"},
    "col_elev":              {"it": "↑ ELEV.",                    "en": "↑ ELEV.",               "de": "↑ HÖHE",                 "fr": "↑ DÉNI.",                "es": "↑ DESNIV."},

    # ── Charts per year ────────────────────────────────────────────────────────
    "chart_km_per_year":     {"it": "KM PER ANNO",               "en": "KM PER YEAR",           "de": "KM PRO JAHR",            "fr": "KM PAR ANNÉE",           "es": "KM POR AÑO"},
    "chart_runs_per_year":   {"it": "CORSE PER ANNO",            "en": "RUNS PER YEAR",         "de": "LÄUFE PRO JAHR",         "fr": "SORTIES PAR ANNÉE",      "es": "CARRERAS POR AÑO"},
    "section_km_per_year":   {"it": "KM PER ANNO",               "en": "KM PER YEAR",           "de": "KM PRO JAHR",            "fr": "KM PAR ANNÉE",           "es": "KM POR AÑO"},
    "axis_n_runs":           {"it": "n. corse",                  "en": "no. of runs",           "de": "Anzahl Läufe",           "fr": "nb sorties",             "es": "n.º carreras"},

    # ── Activity heatmap ──────────────────────────────────────────────────────
    "section_heatmap":       {"it": "HEATMAP ATTIVITÀ — ultime 52 settimane", "en": "ACTIVITY HEATMAP — last 52 weeks", "de": "AKTIVITÄTS-HEATMAP — letzte 52 Wochen", "fr": "CARTE DE CHALEUR — 52 dernières semaines", "es": "MAPA DE CALOR — últimas 52 semanas"},
    "heatmap_rest":          {"it": "riposo",                    "en": "rest",                  "de": "Ruhe",                   "fr": "repos",                  "es": "descanso"},
    "days_short": {
        "it": ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"],
        "en": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "de": ["Mo",  "Di",  "Mi",  "Do",  "Fr",  "Sa",  "So"],
        "fr": ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"],
        "es": ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"],
    },
    "months_short": {
        "it": ["", "Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set", "Ott", "Nov", "Dic"],
        "en": ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "de": ["", "Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"],
        "fr": ["", "Jan", "Fév", "Mar", "Avr", "Mai", "Juin","Juil","Aoû", "Sep", "Oct", "Nov", "Déc"],
        "es": ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
    },
    "months_long": {
        "it": ["","Gennaio","Febbraio","Marzo","Aprile","Maggio","Giugno","Luglio","Agosto","Settembre","Ottobre","Novembre","Dicembre"],
        "en": ["","January","February","March","April","May","June","July","August","September","October","November","December"],
        "de": ["","Januar","Februar","März","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"],
        "fr": ["","Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Août","Septembre","Octobre","Novembre","Décembre"],
        "es": ["","Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"],
    },
    "days_long": {
        "it": ["LUN", "MAR", "MER", "GIO", "VEN", "SAB", "DOM"],
        "en": ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"],
        "de": ["MO",  "DI",  "MI",  "DO",  "FR",  "SA",  "SO"],
        "fr": ["LUN", "MAR", "MER", "JEU", "VEN", "SAM", "DIM"],
        "es": ["LUN", "MAR", "MIÉ", "JUE", "VIE", "SÁB", "DOM"],
    },

    # ── Athlete radar ─────────────────────────────────────────────────────────
    "section_athlete_profile": {"it": "PROFILO ATLETICO",        "en": "ATHLETIC PROFILE",      "de": "ATHLETISCHES PROFIL",    "fr": "PROFIL ATHLÉTIQUE",      "es": "PERFIL ATLÉTICO"},
    "radar_speed":             {"it": "Velocita'",               "en": "Speed",                 "de": "Geschwindigkeit",        "fr": "Vitesse",                "es": "Velocidad"},
    "radar_endurance":         {"it": "Fondo",                   "en": "Endurance",             "de": "Ausdauer",               "fr": "Endurance",              "es": "Fondo"},
    "radar_elevation":         {"it": "Dislivello",              "en": "Elevation",             "de": "Höhenprofil",            "fr": "Dénivelé",               "es": "Desnivel"},
    "radar_consistency":       {"it": "Costanza",                "en": "Consistency",           "de": "Konstanz",               "fr": "Régularité",             "es": "Constancia"},
    "radar_volume":            {"it": "Volume",                  "en": "Volume",                "de": "Volumen",                "fr": "Volume",                 "es": "Volumen"},
    "radar_progress":          {"it": "Progressione",            "en": "Progression",           "de": "Fortschritt",            "fr": "Progression",            "es": "Progresión"},
    "radar_how_calculated":    {"it": "COME SI CALCOLANO LE DIMENSIONI", "en": "HOW DIMENSIONS ARE CALCULATED", "de": "SO WERDEN DIMENSIONEN BERECHNET", "fr": "COMMENT LES DIMENSIONS SONT CALCULÉES", "es": "CÓMO SE CALCULAN LAS DIMENSIONES"},
    "radar_desc_speed":        {"it": "Passo medio di tutte le corse\n(scala 2–5 m/s, 8:20/km → 3:20/km)", "en": "Avg pace of all runs\n(scale 2–5 m/s, 8:20/km → 3:20/km)", "de": "Ø Tempo aller Läufe\n(Skala 2–5 m/s, 8:20/km → 3:20/km)", "fr": "Allure moy. de toutes les sorties\n(échelle 2–5 m/s, 8:20/km → 3:20/km)", "es": "Ritmo medio de todas las carreras\n(escala 2–5 m/s, 8:20/km → 3:20/km)"},
    "radar_desc_endurance":    {"it": "Mediana delle distanze percorse\n(scala 3–42 km)", "en": "Median distance run\n(scale 3–42 km)", "de": "Median der zurückgelegten Distanzen\n(Skala 3–42 km)", "fr": "Médiane des distances parcourues\n(échelle 3–42 km)", "es": "Mediana de distancias recorridas\n(escala 3–42 km)"},
    "radar_desc_elevation":    {"it": "Media del dislivello positivo per km\n(scala 0–40 m/km)", "en": "Avg positive elevation per km\n(scale 0–40 m/km)", "de": "Ø Anstieg pro km\n(Skala 0–40 m/km)", "fr": "Dénivelé positif moy. par km\n(échelle 0–40 m/km)", "es": "Desnivel positivo medio por km\n(escala 0–40 m/km)"},
    "radar_desc_consistency":  {"it": "% settimane con almeno 1 corsa\nnelle ultime 52 settimane", "en": "% weeks with at least 1 run\nin the last 52 weeks", "de": "% Wochen mit mind. 1 Lauf\nin den letzten 52 Wochen", "fr": "% semaines avec au moins 1 sortie\nau cours des 52 dernières semaines", "es": "% semanas con al menos 1 carrera\nen las últimas 52 semanas"},
    "radar_desc_volume":       {"it": "Media km/settimana nelle ultime 52 sett.\n(scala 0–70 km/sett.)", "en": "Avg km/week over the last 52 weeks\n(scale 0–70 km/week)", "de": "Ø km/Woche in den letzten 52 Wochen\n(Skala 0–70 km/Woche)", "fr": "Km/sem. moy. sur les 52 dernières sem.\n(échelle 0–70 km/sem.)", "es": "Km/semana med. en las últimas 52 sem.\n(escala 0–70 km/semana)"},
    "radar_desc_progress":     {"it": "Confronto passo medio: ultimi 3 mesi\nvs 3 mesi precedenti", "en": "Avg pace comparison: last 3 months\nvs previous 3 months", "de": "Ø Tempo-Vergleich: letzte 3 Monate\nvs. vorherige 3 Monate", "fr": "Comparaison allure moy. : 3 derniers mois\nvs 3 mois précédents", "es": "Comparación ritmo medio: últimos 3 meses\nvs 3 meses anteriores"},

    # ── Annual goal ───────────────────────────────────────────────────────────
    "section_annual_goal":   {"it": "OBIETTIVO ANNUALE KM",    "en": "ANNUAL KM GOAL",        "de": "JAHRES-KM-ZIEL",         "fr": "OBJECTIF KM ANNUEL",     "es": "OBJETIVO KM ANUAL"},
    "annual_goal_label":     {"it": "Obiettivo km:",           "en": "Goal km:",               "de": "Ziel km:",               "fr": "Objectif km :",          "es": "Objetivo km:"},
    "btn_save":              {"it": "💾 Salva",                "en": "💾 Save",                "de": "💾 Speichern",           "fr": "💾 Enregistrer",         "es": "💾 Guardar"},
    "annual_goal_run":       {"it": "corsa",                   "en": "run",                    "de": "Lauf",                   "fr": "sortie",                 "es": "carrera"},
    "annual_goal_runs":      {"it": "corse",                   "en": "runs",                   "de": "Läufe",                  "fr": "sorties",                "es": "carreras"},

    # ── Monthly stats ─────────────────────────────────────────────────────────
    "section_monthly":       {"it": "STATISTICHE ULTIMI 12 MESI", "en": "LAST 12 MONTHS STATISTICS", "de": "STATISTIKEN LETZTE 12 MONATE", "fr": "STATISTIQUES 12 DERNIERS MOIS", "es": "ESTADÍSTICAS ÚLTIMOS 12 MESES"},
    "col_month":             {"it": "MESE",   "en": "MONTH",  "de": "MONAT",  "fr": "MOIS",   "es": "MES"},

    # ── Training load ─────────────────────────────────────────────────────────
    "section_training_load": {"it": "CARICO DI ALLENAMENTO",   "en": "TRAINING LOAD",         "de": "TRAININGSBELASTUNG",     "fr": "CHARGE D'ENTRAÎNEMENT",  "es": "CARGA DE ENTRENAMIENTO"},
    "training_load_atl":     {"it": "ATL (Fatica acuta)",       "en": "ATL (Acute fatigue)",   "de": "ATL (Akute Ermüdung)",   "fr": "ATL (Fatigue aiguë)",    "es": "ATL (Fatiga aguda)"},
    "training_load_ctl":     {"it": "CTL (Forma cronica)",      "en": "CTL (Chronic fitness)", "de": "CTL (Chronische Form)",  "fr": "CTL (Forme chronique)",  "es": "CTL (Forma crónica)"},
    "training_load_tsb":     {"it": "TSB (Forma/Freschezza)",   "en": "TSB (Form/Freshness)",  "de": "TSB (Form/Frische)",     "fr": "TSB (Forme/Fraîcheur)",  "es": "TSB (Forma/Frescura)"},

    # ── Grade analysis ────────────────────────────────────────────────────────
    "section_grade":         {"it": "ANALISI PENDENZA",         "en": "GRADE ANALYSIS",        "de": "STEIGUNGSANALYSE",       "fr": "ANALYSE DU DÉNIVELÉ",    "es": "ANÁLISIS DE PENDIENTE"},

    # ── Performance curve ─────────────────────────────────────────────────────
    "section_perf_curve":    {"it": "CURVA DI PERFORMANCE",     "en": "PERFORMANCE CURVE",     "de": "LEISTUNGSKURVE",         "fr": "COURBE DE PERFORMANCE",  "es": "CURVA DE RENDIMIENTO"},

    # ── Race prediction ────────────────────────────────────────────────────────
    "section_race_pred":     {"it": "PREVISIONE PRESTAZIONI",   "en": "PERFORMANCE PREDICTION","de": "LEISTUNGSVORHERSAGE",    "fr": "PRÉVISION DE PERFORMANCE","es": "PREDICCIÓN DE RENDIMIENTO"},

    # ── Distribution ──────────────────────────────────────────────────────────
    "section_dist_distrib":  {"it": "DISTRIBUZIONE DISTANZE",   "en": "DISTANCE DISTRIBUTION", "de": "DISTANZVERTEILUNG",      "fr": "DISTRIBUTION DES DISTANCES","es": "DISTRIBUCIÓN DE DISTANCIAS"},

    # ── Personal records ──────────────────────────────────────────────────────
    "section_personal_records": {"it": "RECORD PERSONALI",      "en": "PERSONAL RECORDS",      "de": "PERSÖNLICHE REKORDE",    "fr": "RECORDS PERSONNELS",     "es": "RÉCORDS PERSONALES"},
    "col_distance_label":    {"it": "DISTANZA",                 "en": "DISTANCE",              "de": "DISTANZ",                "fr": "DISTANCE",               "es": "DISTANCIA"},
    "col_time_label":        {"it": "TEMPO",                    "en": "TIME",                  "de": "ZEIT",                   "fr": "TEMPS",                  "es": "TIEMPO"},
    "col_activity":          {"it": "ATTIVITÀ",                 "en": "ACTIVITY",              "de": "AKTIVITÄT",              "fr": "ACTIVITÉ",               "es": "ACTIVIDAD"},
    "col_date_label":        {"it": "DATA",                     "en": "DATE",                  "de": "DATUM",                  "fr": "DATE",                   "es": "FECHA"},
    "no_data_label":         {"it": "nessun dato",              "en": "no data",               "de": "keine Daten",            "fr": "aucune donnée",          "es": "sin datos"},
    "pr_half_marathon":      {"it": "Mezza Maratona",           "en": "Half Marathon",         "de": "Halbmarathon",           "fr": "Semi-marathon",          "es": "Media Maratón"},
    "pr_marathon":           {"it": "Maratona",                 "en": "Marathon",              "de": "Marathon",               "fr": "Marathon",               "es": "Maratón"},

    # ── Hint for missing records ───────────────────────────────────────────────
    "hint_no_efforts":       {"it": "  Nessun best effort trovato. Le corse scaricate con activity:read_all\n  includono automaticamente i best efforts.", "en": "  No best efforts found. Runs downloaded with activity:read_all\n  automatically include best efforts.", "de": "  Keine Bestleistungen gefunden. Mit activity:read_all heruntergeladene Läufe\n  enthalten automatisch Bestleistungen.", "fr": "  Aucune meilleure performance trouvée. Les sorties téléchargées avec activity:read_all\n  incluent automatiquement les meilleures performances.", "es": "  No se encontraron mejores marcas. Las carreras descargadas con activity:read_all\n  incluyen automáticamente las mejores marcas."},

    # ── VDOT analysis ─────────────────────────────────────────────────────────
    "section_vdot":          {"it": "ANALISI GARE E VDOT",      "en": "RACE ANALYSIS & VDOT",  "de": "RENNANALYSE & VDOT",     "fr": "ANALYSE COURSES & VDOT", "es": "ANÁLISIS CARRERAS Y VDOT"},
    "vdot_total_races":      {"it": "Gare totali",              "en": "Total races",           "de": "Rennen gesamt",          "fr": "Courses totales",        "es": "Carreras totales"},
    "vdot_best":             {"it": "VDOT migliore",            "en": "Best VDOT",             "de": "Bestes VDOT",            "fr": "Meilleur VDOT",          "es": "Mejor VDOT"},
    "vdot_recent":           {"it": "VDOT recente",             "en": "Recent VDOT",           "de": "Aktuelles VDOT",         "fr": "VDOT récent",            "es": "VDOT reciente"},
    "vdot_evolution":        {"it": "EVOLUZIONE VDOT",          "en": "VDOT EVOLUTION",        "de": "VDOT-ENTWICKLUNG",       "fr": "ÉVOLUTION VDOT",         "es": "EVOLUCIÓN VDOT"},
    "vdot_predictions":      {"it": "PREVISIONI",               "en": "PREDICTIONS",           "de": "VORHERSAGEN",            "fr": "PRÉVISIONS",             "es": "PREDICCIONES"},
    "vdot_from":             {"it": "da:",                      "en": "from:",                 "de": "von:",                   "fr": "de :",                   "es": "de:"},
    "vdot_half":             {"it": "Mezza",                    "en": "Half",                  "de": "Halbmarathon",           "fr": "Semi",                   "es": "Media"},
    "vdot_marathon":         {"it": "Maratona",                 "en": "Marathon",              "de": "Marathon",               "fr": "Marathon",               "es": "Maratón"},
    "col_race":              {"it": "GARA",                     "en": "RACE",                  "de": "RENNEN",                 "fr": "COURSE",                 "es": "CARRERA"},

    # ── Recurring routes ─────────────────────────────────────────────────────
    "section_recurring_routes": {"it": "PERCORSI RICORRENTI",   "en": "RECURRING ROUTES",      "de": "WIEDERKEHRENDE ROUTEN",  "fr": "ITINÉRAIRES RÉCURRENTS", "es": "RUTAS RECURRENTES"},
    "recurring_none":        {"it": "  Nessun percorso ricorrente trovato (minimo 3 corse sullo stesso tracciato).", "en": "  No recurring routes found (minimum 3 runs on the same track).", "de": "  Keine wiederkehrenden Routen gefunden (mindestens 3 Läufe auf derselben Strecke).", "fr": "  Aucun itinéraire récurrent trouvé (minimum 3 sorties sur le même tracé).", "es": "  No se encontraron rutas recurrentes (mínimo 3 carreras en el mismo trazado)."},
    "recurring_select_hint": {"it": "← Seleziona un percorso per vedere l'andamento del passo", "en": "← Select a route to see the pace trend", "de": "← Route auswählen, um das Tempoprofil zu sehen", "fr": "← Sélectionnez un itinéraire pour voir l'évolution de l'allure", "es": "← Selecciona una ruta para ver la evolución del ritmo"},
    "recurring_routes_count": {"it": "{n} percorsi  (min. 3 corse)", "en": "{n} routes  (min. 3 runs)", "de": "{n} Routen  (min. 3 Läufe)", "fr": "{n} itinéraires  (min. 3 sorties)", "es": "{n} rutas  (mín. 3 carreras)"},
    "trend_improved":        {"it": "↑ migliorato di {sec}s/km", "en": "↑ improved by {sec}s/km",  "de": "↑ verbessert um {sec}s/km", "fr": "↑ amélioré de {sec}s/km", "es": "↑ mejorado en {sec}s/km"},
    "trend_worsened":        {"it": "↓ peggiorato di {sec}s/km", "en": "↓ worsened by {sec}s/km",  "de": "↓ verschlechtert um {sec}s/km", "fr": "↓ dégradé de {sec}s/km", "es": "↓ empeorado en {sec}s/km"},
    "trend_stable":          {"it": "→ stabile",                 "en": "→ stable",                  "de": "→ stabil",                 "fr": "→ stable",                "es": "→ estable"},
    "best_run":              {"it": "Miglior corsa",             "en": "Best run",                  "de": "Bester Lauf",              "fr": "Meilleure sortie",        "es": "Mejor carrera"},
    "last_run":              {"it": "Ultima corsa",              "en": "Last run",                  "de": "Letzter Lauf",             "fr": "Dernière sortie",         "es": "Última carrera"},
    "best_pace_label":       {"it": "miglior passo",             "en": "best pace",                 "de": "bestes Tempo",             "fr": "meilleure allure",        "es": "mejor ritmo"},
    "avg_pace_label":        {"it": "media",                     "en": "avg",                       "de": "Durchschn.",               "fr": "moy.",                    "es": "media"},
    "btn_map":               {"it": "📍 Mappa",                  "en": "📍 Map",                    "de": "📍 Karte",                  "fr": "📍 Carte",                "es": "📍 Mapa"},
    "insufficient_data":     {"it": "Dati insufficienti per il grafico.", "en": "Insufficient data for chart.", "de": "Unzureichende Daten für das Diagramm.", "fr": "Données insuffisantes pour le graphique.", "es": "Datos insuficientes para el gráfico."},

    # ── Splits tab ────────────────────────────────────────────────────────────
    "splits_title":          {"it": "SPLITS PER CHILOMETRO",    "en": "SPLITS PER KILOMETRE",  "de": "SPLITS PRO KILOMETER",   "fr": "SPLITS PAR KILOMÈTRE",   "es": "PARCIALES POR KILÓMETRO"},
    "col_km":                {"it": "KM",        "en": "KM",       "de": "KM",       "fr": "KM",       "es": "KM"},
    "col_speed":             {"it": "VELOCITÀ",  "en": "SPEED",    "de": "TEMPO",    "fr": "VITESSE",  "es": "VELOCIDAD"},
    "col_elevation":         {"it": "DISLIVELLO","en": "ELEVATION","de": "HÖHENDIFF.","fr": "DÉNIVELÉ","es": "DESNIVEL"},
    "col_cadence":           {"it": "CADENZA",   "en": "CADENCE",  "de": "KADENZ",   "fr": "CADENCE",  "es": "CADENCIA"},
    "col_distance_label":    {"it": "DISTANZA",  "en": "DISTANCE", "de": "DISTANZ",  "fr": "DISTANCE", "es": "DISTANCIA"},
    "splits_total":          {"it": "TOT",       "en": "TOT",      "de": "GES.",     "fr": "TOT",      "es": "TOT"},
    "no_split_data":         {"it": "Nessun dato split disponibile.", "en": "No split data available.", "de": "Keine Split-Daten verfügbar.", "fr": "Aucune donnée de split disponible.", "es": "No hay datos de parciales disponibles."},

    # ── Best efforts ──────────────────────────────────────────────────────────
    "best_title":            {"it": "BEST EFFORTS",             "en": "BEST EFFORTS",          "de": "BESTLEISTUNGEN",         "fr": "MEILLEURES PERFORMANCES","es": "MEJORES MARCAS"},
    "no_best_efforts":       {"it": "Nessun best effort registrato.", "en": "No best efforts recorded.", "de": "Keine Bestleistungen aufgezeichnet.", "fr": "Aucune meilleure performance enregistrée.", "es": "No hay mejores marcas registradas."},
    "pr_badge":              {"it": "🏆 RECORD PERSONALE",      "en": "🏆 PERSONAL RECORD",    "de": "🏆 PERSÖNLICHER REKORD", "fr": "🏆 RECORD PERSONNEL",    "es": "🏆 RÉCORD PERSONAL"},
    "pr_rank":               {"it": "#{n} personale",           "en": "#{n} personal",         "de": "#{n} persönlich",        "fr": "#{n} personnel",         "es": "#{n} personal"},

    # ── Raw JSON tab ──────────────────────────────────────────────────────────
    "raw_title":             {"it": "JSON GREZZO DELL'ATTIVITÀ", "en": "RAW ACTIVITY JSON",    "de": "ROHE AKTIVITÄTS-JSON",   "fr": "JSON BRUT DE L'ACTIVITÉ","es": "JSON CRUDO DE LA ACTIVIDAD"},

    # ── Map tab ───────────────────────────────────────────────────────────────
    "map_no_folium":         {"it": "⚠️  Installa folium per la mappa:\n  pip install folium", "en": "⚠️  Install folium for the map:\n  pip install folium", "de": "⚠️  Folium installieren:\n  pip install folium", "fr": "⚠️  Installez folium pour la carte :\n  pip install folium", "es": "⚠️  Instala folium para el mapa:\n  pip install folium"},
    "map_no_gps":            {"it": "⚠️  Nessun dato GPS disponibile.\n\nLa polyline richiede il permesso Strava «activity:read_all».", "en": "⚠️  No GPS data available.\n\nThe polyline requires the Strava permission «activity:read_all».", "de": "⚠️  Keine GPS-Daten verfügbar.\n\nDie Polylinie erfordert die Strava-Berechtigung «activity:read_all».", "fr": "⚠️  Aucune donnée GPS disponible.\n\nLa polyligne nécessite la permission Strava «activity:read_all».", "es": "⚠️  Sin datos GPS disponibles.\n\nLa polilínea requiere el permiso de Strava «activity:read_all»."},
    "map_gps_points":        {"it": "punti GPS",                "en": "GPS points",            "de": "GPS-Punkte",             "fr": "points GPS",             "es": "puntos GPS"},
    "map_generating":        {"it": "⏳ Generazione mappa…",    "en": "⏳ Generating map…",    "de": "⏳ Karte wird erstellt…", "fr": "⏳ Génération de la carte…","es": "⏳ Generando mapa…"},
    "map_open_browser":      {"it": "🗺  Apri mappa nel browser","en": "🗺  Open map in browser","de": "🗺  Karte im Browser öffnen","fr": "🗺  Ouvrir la carte dans le navigateur","es": "🗺  Abrir mapa en el navegador"},
    "map_reopen":            {"it": "🗺  Riapri nel browser",   "en": "🗺  Reopen in browser", "de": "🗺  Im Browser erneut öffnen","fr": "🗺  Rouvrir dans le navigateur","es": "🗺  Reabrir en el navegador"},
    "map_opened":            {"it": "✅ Mappa aperta nel browser.","en": "✅ Map opened in browser.","de": "✅ Karte im Browser geöffnet.","fr": "✅ Carte ouverte dans le navigateur.","es": "✅ Mapa abierto en el navegador."},
    "map_error":             {"it": "❌ Errore: {e}",           "en": "❌ Error: {e}",          "de": "❌ Fehler: {e}",          "fr": "❌ Erreur : {e}",         "es": "❌ Error: {e}"},
    "map_hint":              {"it": "La mappa viene aperta nel browser predefinito", "en": "The map opens in your default browser", "de": "Die Karte wird im Standardbrowser geöffnet", "fr": "La carte s'ouvre dans votre navigateur par défaut", "es": "El mapa se abre en el navegador predeterminado"},
    "map_fullscreen":        {"it": "Schermo intero",           "en": "Fullscreen",            "de": "Vollbild",               "fr": "Plein écran",             "es": "Pantalla completa"},
    "map_exit_fullscreen":   {"it": "Esci da schermo intero",  "en": "Exit fullscreen",       "de": "Vollbild beenden",       "fr": "Quitter le plein écran",  "es": "Salir de pantalla completa"},
    "map_start":             {"it": "▶ Inizio",                "en": "▶ Start",               "de": "▶ Start",                "fr": "▶ Départ",                "es": "▶ Inicio"},
    "map_finish":            {"it": "⏹ Arrivo",                "en": "⏹ Finish",              "de": "⏹ Ziel",                 "fr": "⏹ Arrivée",               "es": "⏹ Llegada"},
    "map_total":             {"it": "⏱ totale",                "en": "⏱ total",               "de": "⏱ gesamt",               "fr": "⏱ total",                 "es": "⏱ total"},
    "map_max":               {"it": "max",                     "en": "max",                   "de": "max",                    "fr": "max",                     "es": "máx."},
    "map_suffer":            {"it": "💢 Suffer score:",         "en": "💢 Suffer score:",      "de": "💢 Belastungsscore:",     "fr": "💢 Score effort :",       "es": "💢 Índice esfuerzo:"},
    "map_pace_km":           {"it": "Passo:",                  "en": "Pace:",                 "de": "Tempo:",                 "fr": "Allure :",                "es": "Ritmo:"},
    "map_fc":                {"it": "FC:",                     "en": "HR:",                   "de": "HF:",                    "fr": "FC :",                    "es": "FC:"},
    "map_elevation_delta":   {"it": "Δalt:",                   "en": "Δalt:",                 "de": "ΔHöhe:",                 "fr": "Δalt :",                  "es": "Δalt:"},
    "map_light_tile":        {"it": "Chiaro",                  "en": "Light",                 "de": "Hell",                   "fr": "Clair",                   "es": "Claro"},

    # ── HR zones tab ──────────────────────────────────────────────────────────
    "hr_max_label":          {"it": "FC MASSIMA:",             "en": "MAX HR:",               "de": "MAX HF:",                "fr": "FC MAX :",                "es": "FC MÁX:"},
    "btn_update":            {"it": "AGGIORNA",                "en": "UPDATE",                "de": "AKTUALISIEREN",          "fr": "ACTUALISER",              "es": "ACTUALIZAR"},
    "hr_hint":               {"it": "(Modifica la FC max per ricalcolare le zone)", "en": "(Edit max HR to recalculate zones)", "de": "(Max HF bearbeiten, um Zonen neu zu berechnen)", "fr": "(Modifiez la FC max pour recalculer les zones)", "es": "(Edita la FC máx. para recalcular las zonas)"},
    "hr_info_title":         {"it": "Come leggere i grafici delle Zone HR", "en": "How to read HR Zone charts", "de": "HR-Zonen-Diagramme lesen", "fr": "Comment lire les graphiques des zones FC", "es": "Cómo leer los gráficos de zonas FC"},
    "chart_hr_zones":        {"it": "DISTRIBUZIONE ZONE CARDIACHE", "en": "HEART RATE ZONE DISTRIBUTION", "de": "HERZFREQUENZ-ZONENVERTEILUNG", "fr": "DISTRIBUTION DES ZONES CARDIAQUES", "es": "DISTRIBUCIÓN DE ZONAS CARDÍACAS"},
    "axis_pct_time":         {"it": "% del tempo",             "en": "% of time",             "de": "% der Zeit",             "fr": "% du temps",              "es": "% del tiempo"},
    "hr_max_annotation":     {"it": "FC max: {val} bpm",       "en": "Max HR: {val} bpm",     "de": "Max HF: {val} bpm",      "fr": "FC max : {val} bpm",      "es": "FC máx.: {val} bpm"},
    "chart_hr_scatter":      {"it": "SCATTER: FC vs PASSO",    "en": "SCATTER: HR vs PACE",   "de": "STREUDIAGRAMM: HF vs. TEMPO", "fr": "NUAGE: FC vs ALLURE",  "es": "DISPERSIÓN: FC vs RITMO"},
    "axis_hr_bpm":           {"it": "Frequenza cardiaca (bpm)","en": "Heart rate (bpm)",      "de": "Herzfrequenz (bpm)",     "fr": "Fréquence cardiaque (bpm)","es": "Frecuencia cardíaca (bpm)"},
    "axis_pace_minkm":       {"it": "Passo (min/km)",          "en": "Pace (min/km)",         "de": "Tempo (min/km)",         "fr": "Allure (min/km)",         "es": "Ritmo (min/km)"},
    "hr_trend":              {"it": "Tendenza",                "en": "Trend",                 "de": "Trend",                  "fr": "Tendance",                "es": "Tendencia"},
    "hr_zones_label":        {"it": "Zone HR",                 "en": "HR Zones",              "de": "HF-Zonen",               "fr": "Zones FC",                "es": "Zonas FC"},
    "chart_hr_analysis":     {"it": "Analisi zone cardiache  •  {name}", "en": "Heart rate zone analysis  •  {name}", "de": "Herzfrequenz-Zonenanalyse  •  {name}", "fr": "Analyse zones cardiaques  •  {name}", "es": "Análisis zonas cardíacas  •  {name}"},
    "hr_insufficient":       {"it": "Dati insufficienti",      "en": "Insufficient data",     "de": "Unzureichende Daten",    "fr": "Données insuffisantes",   "es": "Datos insuficientes"},
    "no_hr_data":            {"it": "Nessun dato di frequenza cardiaca disponibile.", "en": "No heart rate data available.", "de": "Keine Herzfrequenzdaten verfügbar.", "fr": "Aucune donnée de fréquence cardiaque disponible.", "es": "Sin datos de frecuencia cardíaca disponibles."},

    # ── Charts tab ────────────────────────────────────────────────────────────
    "chart_pace_per_km":     {"it": "PASSO PER CHILOMETRO",    "en": "PACE PER KILOMETRE",    "de": "TEMPO PRO KILOMETER",    "fr": "ALLURE PAR KILOMÈTRE",   "es": "RITMO POR KILÓMETRO"},
    "chart_speed":           {"it": "VELOCITÀ (km/h)",         "en": "SPEED (km/h)",          "de": "GESCHWINDIGKEIT (km/h)", "fr": "VITESSE (km/h)",          "es": "VELOCIDAD (km/h)"},
    "chart_elev_per_km":     {"it": "DISLIVELLO PER KM",       "en": "ELEVATION PER KM",      "de": "HÖHENUNTERSCHIED/KM",    "fr": "DÉNIVELÉ PAR KM",        "es": "DESNIVEL POR KM"},
    "chart_hr":              {"it": "FREQUENZA CARDIACA",      "en": "HEART RATE",            "de": "HERZFREQUENZ",           "fr": "FRÉQUENCE CARDIAQUE",     "es": "FRECUENCIA CARDÍACA"},
    "chart_cadence":         {"it": "CADENZA (passi/min)",     "en": "CADENCE (steps/min)",   "de": "KADENZ (Schritte/min)",  "fr": "CADENCE (pas/min)",       "es": "CADENCIA (pasos/min)"},
    "chart_pace_faster":     {"it": "Più veloce della media",  "en": "Faster than average",  "de": "Schneller als Durchschnitt","fr": "Plus rapide que la moy.","es": "Más rápido que la media"},
    "chart_pace_avg":        {"it": "In media",                "en": "On average",            "de": "Im Durchschnitt",        "fr": "Dans la moyenne",         "es": "En la media"},
    "chart_pace_slower":     {"it": "Più lento della media",   "en": "Slower than average",  "de": "Langsamer als Durchschnitt","fr": "Plus lent que la moy.", "es": "Más lento que la media"},
    "chart_pace_avg_line":   {"it": "Media",                   "en": "Avg",                   "de": "Durchschn.",             "fr": "Moy.",                    "es": "Media"},
    "chart_no_splits":       {"it": "Nessun dato split disponibile.", "en": "No split data available.", "de": "Keine Split-Daten verfügbar.", "fr": "Aucune donnée de split disponible.", "es": "No hay datos de parciales disponibles."},

    # ── Compare tab ────────────────────────────────────────────────────────────
    "compare_title":         {"it": "CONFRONTO  ({n} ATTIVITÀ)", "en": "COMPARE  ({n} ACTIVITIES)", "de": "VERGLEICH  ({n} AKTIVITÄTEN)", "fr": "COMPARAISON  ({n} ACTIVITÉS)", "es": "COMPARACIÓN  ({n} ACTIVIDADES)"},
    "compare_main":          {"it": "[Principale]  ",           "en": "[Main]  ",              "de": "[Haupt]  ",              "fr": "[Principal]  ",           "es": "[Principal]  "},
    "section_cmp_stats":     {"it": "STATISTICHE A CONFRONTO",  "en": "COMPARATIVE STATISTICS","de": "VERGLEICHSSTATISTIKEN",  "fr": "STATISTIQUES COMPARÉES",  "es": "ESTADÍSTICAS COMPARADAS"},
    "cmp_metric":            {"it": "METRICA",                  "en": "METRIC",                "de": "METRIK",                 "fr": "MÉTRIQUE",                "es": "MÉTRICA"},
    "cmp_distance":          {"it": "Distanza",                 "en": "Distance",              "de": "Distanz",                "fr": "Distance",                "es": "Distancia"},
    "cmp_moving_time":       {"it": "Tempo attivo",             "en": "Moving time",           "de": "Bewegungszeit",          "fr": "Temps actif",             "es": "Tiempo activo"},
    "cmp_total_time":        {"it": "Tempo totale",             "en": "Total time",            "de": "Gesamtzeit",             "fr": "Temps total",             "es": "Tiempo total"},
    "cmp_avg_pace":          {"it": "Passo medio",              "en": "Avg pace",              "de": "Ø Tempo",                "fr": "Allure moy.",             "es": "Ritmo medio"},
    "cmp_best_pace":         {"it": "Passo migliore",           "en": "Best pace",             "de": "Besttempo",              "fr": "Meilleure allure",        "es": "Mejor ritmo"},
    "cmp_avg_speed":         {"it": "Velocità media",           "en": "Avg speed",             "de": "Ø Geschwindigkeit",      "fr": "Vitesse moy.",            "es": "Velocidad media"},
    "cmp_elev":              {"it": "Dislivello +",             "en": "Elevation gain",        "de": "Höhengewinn",            "fr": "Dénivelé +",              "es": "Desnivel +"},
    "cmp_avg_hr":            {"it": "HR media",                 "en": "Avg HR",                "de": "Ø Herzfrequenz",         "fr": "FC moy.",                 "es": "FC media"},
    "cmp_max_hr":            {"it": "HR massima",               "en": "Max HR",                "de": "Max Herzfrequenz",       "fr": "FC max.",                 "es": "FC máx."},
    "cmp_calories":          {"it": "Calorie",                  "en": "Calories",              "de": "Kalorien",               "fr": "Calories",                "es": "Calorías"},
    "cmp_cadence":           {"it": "Cadenza",                  "en": "Cadence",               "de": "Kadenz",                 "fr": "Cadence",                 "es": "Cadencia"},
    "cmp_suffer":            {"it": "Suffer Score",             "en": "Suffer Score",          "de": "Belastungsscore",        "fr": "Score effort",            "es": "Índice esfuerzo"},
    "section_pace_compare":  {"it": "PASSO PER CHILOMETRO — CONFRONTO", "en": "PACE PER KM — COMPARISON", "de": "TEMPO PRO KM — VERGLEICH", "fr": "ALLURE PAR KM — COMPARAISON", "es": "RITMO POR KM — COMPARACIÓN"},
    "section_hr_compare":    {"it": "FREQUENZA CARDIACA PER KM — CONFRONTO", "en": "HEART RATE PER KM — COMPARISON", "de": "HERZFREQUENZ PRO KM — VERGLEICH", "fr": "FC PAR KM — COMPARAISON", "es": "FC POR KM — COMPARACIÓN"},
    "chart_pace_km":         {"it": "Passo km per km",          "en": "Pace km by km",         "de": "Tempo km für km",        "fr": "Allure km par km",        "es": "Ritmo km a km"},
    "chart_hr_km":           {"it": "Frequenza cardiaca km per km", "en": "Heart rate km by km","de": "Herzfrequenz km für km", "fr": "Fréquence cardiaque km par km","es": "FC km a km"},
    "compare_no_activities": {"it": "Nessuna attività da confrontare.\n\nApri un'attività principale, poi aggiungi altre dalla Libreria con ➕.", "en": "No activities to compare.\n\nOpen a main activity, then add others from the Library with ➕.", "de": "Keine Aktivitäten zum Vergleichen.\n\nHauptaktivität öffnen, dann weitere über ➕ in der Bibliothek hinzufügen.", "fr": "Aucune activité à comparer.\n\nOuvrez une activité principale, puis ajoutez-en d'autres depuis la bibliothèque avec ➕.", "es": "No hay actividades para comparar.\n\nAbre una actividad principal, luego añade otras desde la Biblioteca con ➕."},

    # ── Calendar tab ──────────────────────────────────────────────────────────
    "calendar_today":        {"it": "Oggi",   "en": "Today",  "de": "Heute",  "fr": "Aujourd'hui","es": "Hoy"},
    "calendar_run_singular": {"it": "corsa",  "en": "run",    "de": "Lauf",   "fr": "sortie",    "es": "carrera"},
    "calendar_run_plural":   {"it": "corse",  "en": "runs",   "de": "Läufe",  "fr": "sorties",   "es": "carreras"},

    # ── Downloader ────────────────────────────────────────────────────────────
    "downloader_title":      {"it": "⬇  DOWNLOAD DA STRAVA",   "en": "⬇  DOWNLOAD FROM STRAVA","de": "⬇  VON STRAVA LADEN",    "fr": "⬇  TÉLÉCHARGER DE STRAVA","es": "⬇  DESCARGAR DE STRAVA"},
    "downloader_win_title":  {"it": "Download da Strava",      "en": "Download from Strava",  "de": "Von Strava laden",       "fr": "Télécharger de Strava",   "es": "Descargar de Strava"},
    "downloader_creds_hint": {"it": "Inserisci le credenziali della tua app Strava\n(crea l'app su https://www.strava.com/settings/api)", "en": "Enter your Strava app credentials\n(create the app at https://www.strava.com/settings/api)", "de": "Gib deine Strava-App-Zugangsdaten ein\n(App erstellen unter https://www.strava.com/settings/api)", "fr": "Saisissez les identifiants de votre app Strava\n(créez l'app sur https://www.strava.com/settings/api)", "es": "Introduce las credenciales de tu app Strava\n(crea la app en https://www.strava.com/settings/api)"},
    "downloader_save_in":    {"it": "SALVA IN:",               "en": "SAVE TO:",              "de": "SPEICHERN IN:",          "fr": "ENREGISTRER DANS :",      "es": "GUARDAR EN:"},
    "downloader_mongo_off":  {"it": "(MongoDB non connesso)",  "en": "(MongoDB not connected)","de": "(MongoDB nicht verbunden)","fr": "(MongoDB non connecté)", "es": "(MongoDB no conectado)"},
    "downloader_new":        {"it": "Nuove: {n}",              "en": "New: {n}",              "de": "Neu: {n}",               "fr": "Nouvelles : {n}",         "es": "Nuevas: {n}"},
    "downloader_skip":       {"it": "Già presenti: {n}",       "en": "Already present: {n}",  "de": "Bereits vorhanden: {n}", "fr": "Déjà présentes : {n}",    "es": "Ya presentes: {n}"},
    "downloader_errors":     {"it": "Errori: {n}",             "en": "Errors: {n}",           "de": "Fehler: {n}",            "fr": "Erreurs : {n}",           "es": "Errores: {n}"},
    "btn_start_download":    {"it": "▶  AVVIA DOWNLOAD",       "en": "▶  START DOWNLOAD",     "de": "▶  DOWNLOAD STARTEN",    "fr": "▶  LANCER LE TÉLÉCHARGEMENT","es": "▶  INICIAR DESCARGA"},
    "btn_downloading":       {"it": "⏳ In corso…",             "en": "⏳ In progress…",        "de": "⏳ In Bearbeitung…",      "fr": "⏳ En cours…",             "es": "⏳ En proceso…"},
    "btn_close":             {"it": "✕  Chiudi",               "en": "✕  Close",              "de": "✕  Schließen",           "fr": "✕  Fermer",               "es": "✕  Cerrar"},
    "downloader_ready":      {"it": "✔ Finestra pronta. Inserisci le credenziali e clicca AVVIA DOWNLOAD.", "en": "✔ Window ready. Enter credentials and click START DOWNLOAD.", "de": "✔ Fenster bereit. Zugangsdaten eingeben und DOWNLOAD STARTEN klicken.", "fr": "✔ Fenêtre prête. Saisissez vos identifiants et cliquez sur LANCER LE TÉLÉCHARGEMENT.", "es": "✔ Ventana lista. Introduce las credenciales y haz clic en INICIAR DESCARGA."},
    "downloader_err_no_cid": {"it": "Inserisci il Client ID.",       "en": "Enter the Client ID.",        "de": "Client-ID eingeben.",        "fr": "Saisissez le Client ID.",      "es": "Introduce el Client ID."},
    "downloader_err_no_csc": {"it": "Inserisci il Client Secret.",   "en": "Enter the Client Secret.",    "de": "Client-Secret eingeben.",    "fr": "Saisissez le Client Secret.",  "es": "Introduce el Client Secret."},
    "downloader_err_no_dst": {"it": "Seleziona almeno una destinazione.", "en": "Select at least one destination.", "de": "Mindestens ein Ziel auswählen.", "fr": "Sélectionnez au moins une destination.", "es": "Selecciona al menos un destino."},

    # ── Export PDF ────────────────────────────────────────────────────────────
    "pdf_splits_header":     {"it": "▸ SPLITS PER CHILOMETRO", "en": "▸ SPLITS PER KILOMETRE","de": "▸ SPLITS PRO KILOMETER", "fr": "▸ SPLITS PAR KILOMÈTRE",  "es": "▸ PARCIALES POR KILÓMETRO"},
    "pdf_generated_by":      {"it": "Generato da Strava Viewer v3.0", "en": "Generated by Strava Viewer v3.0", "de": "Erstellt von Strava Viewer v3.0", "fr": "Généré par Strava Viewer v3.0", "es": "Generado por Strava Viewer v3.0"},
    "pdf_left_stats": {
        "it": ["Distanza", "Tempo attivo", "Passo medio", "Passo migliore", "Velocità media", "Dislivello +"],
        "en": ["Distance", "Moving time", "Avg pace", "Best pace", "Avg speed", "Elevation gain"],
        "de": ["Distanz", "Bewegungszeit", "Ø Tempo", "Besttempo", "Ø Geschw.", "Höhengewinn"],
        "fr": ["Distance", "Temps actif", "Allure moy.", "Meilleure allure", "Vitesse moy.", "Dénivelé +"],
        "es": ["Distancia", "Tiempo activo", "Ritmo medio", "Mejor ritmo", "Velocidad media", "Desnivel +"],
    },
    "pdf_right_stats": {
        "it": ["HR media", "HR massima", "Calorie", "Cadenza", "Suffer Score", "Device"],
        "en": ["Avg HR", "Max HR", "Calories", "Cadence", "Suffer Score", "Device"],
        "de": ["Ø Herzfrequenz", "Max HF", "Kalorien", "Kadenz", "Belastungsscore", "Gerät"],
        "fr": ["FC moy.", "FC max.", "Calories", "Cadence", "Score effort", "Appareil"],
        "es": ["FC media", "FC máx.", "Calorías", "Cadencia", "Índice esfuerzo", "Dispositivo"],
    },

    # ── HR zone names (list — used in bar chart labels) ───────────────────────
    "hr_zone_names": {
        "it": ["Z1 Recupero", "Z2 Aerobica", "Z3 Soglia", "Z4 Anaerobica", "Z5 Massimale"],
        "en": ["Z1 Recovery", "Z2 Aerobic",  "Z3 Threshold", "Z4 Anaerobic", "Z5 Max"],
        "de": ["Z1 Erholung", "Z2 Aerob",    "Z3 Schwelle",  "Z4 Anaerob",   "Z5 Maximum"],
        "fr": ["Z1 Récupération", "Z2 Aérobie", "Z3 Seuil", "Z4 Anaérobie", "Z5 Maximum"],
        "es": ["Z1 Recuperación", "Z2 Aeróbica","Z3 Umbral","Z4 Anaeróbica","Z5 Máxima"],
    },

    # ── Chart titles ──────────────────────────────────────────────────────────
    "chart_km_per_month":   {"it": "KM PER MESE",                "en": "KM PER MONTH",             "de": "KM PRO MONAT",            "fr": "KM PAR MOIS",              "es": "KM POR MES"},
    "chart_grade_pace":     {"it": "PASSO MEDIANO PER PENDENZA",  "en": "MEDIAN PACE BY GRADIENT",  "de": "MEDIANES TEMPO JE STEIGUNG","fr": "ALLURE MÉDIANE PAR PENTE", "es": "RITMO MEDIANO POR PENDIENTE"},
    "chart_perf_curve_ttl": {"it": "CURVA DI PERFORMANCE — DISTANZA vs TEMPO", "en": "PERFORMANCE CURVE — DISTANCE vs TIME", "de": "LEISTUNGSKURVE — DISTANZ vs ZEIT", "fr": "COURBE DE PERFORMANCE — DISTANCE vs TEMPS", "es": "CURVA DE RENDIMIENTO — DISTANCIA vs TIEMPO"},

    # ── Axis labels ───────────────────────────────────────────────────────────
    "map_tile_light":       {"it": "Mappa chiara",   "en": "Light map",      "de": "Helle Karte",     "fr": "Carte claire",      "es": "Mapa claro"},
    "map_tile_topo":        {"it": "Topografica",    "en": "Topographic",    "de": "Topografisch",    "fr": "Topographique",     "es": "Topográfico"},
    "map_fullscreen":       {"it": "Schermo intero", "en": "Full screen",    "de": "Vollbild",        "fr": "Plein écran",       "es": "Pantalla completa"},
    "map_fullscreen_exit":  {"it": "Esci",           "en": "Exit",           "de": "Beenden",         "fr": "Quitter",           "es": "Salir"},
    "map_select_all":       {"it": "Seleziona tutti",   "en": "Select all",     "de": "Alle auswählen",    "fr": "Tout sélectionner",   "es": "Seleccionar todo"},
    "map_deselect_all":     {"it": "Deseleziona tutti", "en": "Deselect all",   "de": "Alle abwählen",     "fr": "Tout désélectionner", "es": "Deseleccionar todo"},
    "msg_no_gps_tracks":    {"it": "Nessuna traccia GPS disponibile per questo gruppo.", "en": "No GPS tracks available for this group.", "de": "Keine GPS-Spuren für diese Gruppe verfügbar.", "fr": "Aucune trace GPS disponible pour ce groupe.", "es": "No hay trazas GPS disponibles para este grupo."},
    "perf_curve_legend":    {"it": "● best effort effettivo  — curva fit potenza", "en": "● actual best effort  — power fit curve", "de": "● tatsächlicher Bestwert  — Potenz-Fit-Kurve", "fr": "● meilleure perf. réelle  — courbe d'ajustement", "es": "● mejor marca real  — curva de ajuste potencia"},
    "axis_dist_m":          {"it": "Distanza (m)", "en": "Distance (m)", "de": "Distanz (m)", "fr": "Distance (m)", "es": "Distancia (m)"},
    "axis_time_s":          {"it": "Tempo (s)",    "en": "Time (s)",     "de": "Zeit (s)",    "fr": "Temps (s)",    "es": "Tiempo (s)"},

    # ── Period labels ─────────────────────────────────────────────────────────
    "period_last_days":     {"it": "ultimi {n}gg", "en": "last {n} days", "de": "letzte {n} Tage", "fr": "{n} derniers jours", "es": "últimos {n} días"},
    "period_all_history":   {"it": "tutto lo storico", "en": "all history", "de": "gesamte Historie", "fr": "tout l'historique", "es": "todo el historial"},

    # ── Info popup titles ─────────────────────────────────────────────────────
    "info_training_load_title": {"it": "Come leggere il grafico del Carico di Allenamento", "en": "How to read the Training Load chart", "de": "Trainingsbelastungsdiagramm verstehen", "fr": "Comment lire le graphique de charge d'entraînement", "es": "Cómo leer el gráfico de carga de entrenamiento"},
    "info_race_pred_title":     {"it": "Previsione Prestazioni — Come funziona", "en": "Performance Prediction — How it works", "de": "Leistungsvorhersage — So funktioniert es", "fr": "Prévision de performance — Comment ça marche", "es": "Predicción de rendimiento — Cómo funciona"},

    # ── Info popup contents ───────────────────────────────────────────────────
    "info_hr": {
        "it": """\
## GRAFICO 1 — DISTRIBUZIONE ZONE CARDIACHE

Le zone cardiache dividono l'intensità dello sforzo in 5 fasce, calcolate come percentuale della tua FC massima.

# Z1 — RECUPERO  (< 60% FCmax)
Sforzo leggerissimo. Zona del riscaldamento, defaticamento e corsa di recupero attivo. Il corpo brucia prevalentemente grassi. Non affatica, ma favorisce il recupero tra sessioni intense.

# Z2 — AEROBICA  (60–70% FCmax)
La zona d'oro. Qui si costruisce la resistenza di base: il cuore diventa più efficiente, i capillari si moltiplicano. Le corse lunghe "lente" appartengono a questa zona.
NOTA DEL COACH: se non riesci a mantenere una conversazione normale in Z2, stai andando troppo forte.

# Z3 — SOGLIA  (70–80% FCmax)
La zona "comfortably hard". Migliora la soglia anaerobica, ma è anche la più insidiosa: abbastanza faticosa da accumulare stanchezza sistemica, ma non abbastanza intensa da dare i grandi adattamenti della Z4.

# Z4 — ANAEROBICA  (80–90% FCmax)
Lavoro di qualità. Intervalli, ripetute veloci, ritmo gara su distanze brevi (5K–10K). Richiede recupero adeguato (24–48 ore) tra le sessioni.

# Z5 — MASSIMALE  (> 90% FCmax)
Sforzo massimo, sostenibile solo per pochi secondi o minuti. Sviluppa la potenza neuromuscolare e la VO2max.

---

# COME LEGGERE LA TORTA DELLE ZONE
• Distribuzione sana: circa 75–80% in Z1–Z2 e il restante 20–25% in Z3–Z5 (metodo polarizzato).
• Molta Z3 e poca Z4–Z5 = stai correndo "nel mezzo": errore tipico del runner amatore.

## GRAFICO 2 — FC vs PASSO
• Nuvola compatta diagonale: buona efficienza aerobica.
• Cardiac drift: FC sale a passo costante → intensità superiore alla soglia aerobica.
NOTA DEL COACH: confronta le stesse distanze a mesi di distanza. Se la nuvola si sposta a sinistra (stessa FC, passo migliore) stai progredendo.""",
        "en": """\
## CHART 1 — HEART RATE ZONE DISTRIBUTION

Heart rate zones divide exercise intensity into 5 bands, calculated as a percentage of your maximum heart rate.

# Z1 — RECOVERY  (< 60% HRmax)
Very light effort. Zone for warm-up, cool-down and active recovery runs. The body burns primarily fat.

# Z2 — AEROBIC  (60–70% HRmax)
The golden zone. Base endurance is built here: the heart becomes more efficient, capillaries multiply. Long "slow" runs belong to this zone.
COACH NOTE: if you cannot hold a normal conversation while running in Z2, you are going too fast.

# Z3 — THRESHOLD  (70–80% HRmax)
The "comfortably hard" zone. Improves the anaerobic threshold but also accumulates systemic fatigue without delivering the major adaptations of Z4.

# Z4 — ANAEROBIC  (80–90% HRmax)
Quality work. Intervals, fast repetitions, race pace over short distances (5K–10K). Requires adequate recovery (24–48 hours) between sessions.

# Z5 — MAX  (> 90% HRmax)
Maximum effort, sustainable for only seconds or minutes. Develops neuromuscular power and VO2max.

---

# HOW TO READ THE ZONE CHART
• Healthy distribution: ~75–80% in Z1–Z2 and 20–25% in Z3–Z5 (polarised training).
• Lots of Z3 and little Z4–Z5 = running "in the middle": typical amateur mistake.

## CHART 2 — HR vs PACE
• Compact diagonal cloud: good aerobic efficiency.
• Cardiac drift: HR rises at constant pace → intensity above aerobic threshold.
COACH NOTE: compare the same distances run months apart. If the cloud shifts left (same HR, better pace) you are progressing.""",
        "de": """\
## DIAGRAMM 1 — HERZFREQUENZZONENVERTEILUNG

Herzfrequenzzonen teilen die Belastungsintensität in 5 Bereiche ein (% der maximalen HF).

# Z1 — ERHOLUNG  (< 60% HFmax)
Sehr leichte Belastung. Aufwärmen, Abkühlen und aktive Erholung. Hauptsächlich Fettverbrennung.

# Z2 — AEROB  (60–70% HFmax)
Die goldene Zone. Hier wird Grundlagenausdauer aufgebaut.
TRAINER-HINWEIS: Wenn Sie in Z2 kein Gespräch führen können, sind Sie zu schnell.

# Z3 — SCHWELLE  (70–80% HFmax)
Verbessert die anaerobe Schwelle, accumulates systemische Ermüdung.

# Z4 — ANAEROB  (80–90% HFmax)
Qualitätsarbeit: Intervalle, schnelle Wiederholungen. Erfordert 24–48h Erholung.

# Z5 — MAXIMUM  (> 90% HFmax)
Maximale Belastung für Sekunden/Minuten. Entwickelt VO2max und Schnellkraft.

---

# KUCHENDIAGRAMM
• Gesunde Verteilung: 75–80% in Z1–Z2, 20–25% in Z3–Z5 (polarisiertes Training).

## DIAGRAMM 2 — HF vs TEMPO
• Kompakte Wolke: gute aerobe Effizienz. Kardialer Drift = Intensität über aerober Schwelle.""",
        "fr": """\
## GRAPHIQUE 1 — DISTRIBUTION DES ZONES CARDIAQUES

Les zones de FC divisent l'intensité en 5 niveaux (% de la FCmax).

# Z1 — RÉCUPÉRATION  (< 60% FCmax)
Effort très léger. Échauffement, retour au calme, récupération active.

# Z2 — AÉROBIE  (60–70% FCmax)
La zone d'or. L'endurance de base se construit ici.
NOTE DU COACH : si vous ne pouvez pas tenir une conversation en Z2, vous allez trop vite.

# Z3 — SEUIL  (70–80% FCmax)
Zone "agréablement difficile". Améliore le seuil anaérobie.

# Z4 — ANAÉROBIE  (80–90% FCmax)
Travail de qualité : intervalles, répétitions rapides. Récupération 24–48h nécessaire.

# Z5 — MAXIMUM  (> 90% FCmax)
Effort maximal quelques secondes/minutes. Développe le VO2max.

---

# GRAPHIQUE EN SECTEURS
• Distribution saine : 75–80% en Z1–Z2, 20–25% en Z3–Z5 (méthode polarisée).

## GRAPHIQUE 2 — FC vs ALLURE
• Nuage compact diagonal : bonne efficacité aérobie. Dérive cardiaque = seuil dépassé.""",
        "es": """\
## GRÁFICO 1 — DISTRIBUCIÓN DE ZONAS CARDÍACAS

Las zonas de FC dividen la intensidad en 5 rangos (% de la FCmáx).

# Z1 — RECUPERACIÓN  (< 60% FCmáx)
Esfuerzo muy ligero. Calentamiento, vuelta a la calma, recuperación activa.

# Z2 — AERÓBICA  (60–70% FCmáx)
La zona dorada. Aquí se construye la resistencia base.
NOTA: si no puedes conversar en Z2, vas demasiado rápido.

# Z3 — UMBRAL  (70–80% FCmáx)
Mejora el umbral anaeróbico pero acumula fatiga sistémica.

# Z4 — ANAERÓBICA  (80–90% FCmáx)
Trabajo de calidad: intervalos. Requiere 24–48h de recuperación.

# Z5 — MÁXIMA  (> 90% FCmáx)
Esfuerzo máximo sostenible segundos/minutos. Desarrolla VO2máx.

---

# GRÁFICO DE SECTORES
• Distribución saludable: 75–80% en Z1–Z2, 20–25% en Z3–Z5 (método polarizado).

## GRÁFICO 2 — FC vs RITMO
• Nube diagonal compacta: buena eficiencia aeróbica. Deriva cardíaca = umbral superado.""",
    },

    "info_vdot": {
        "it": """\
## VDOT — Indice di Forma di Jack Daniels

Il VDOT è un numero che riassume la tua capacità aerobica ricavato direttamente dai tuoi risultati di gara reali, senza test in laboratorio.

─────────────────────────────────────────────
COME VIENE CALCOLATO
─────────────────────────────────────────────
La formula di Daniels stima la % del VO₂max sostenibile in gara:
  • Velocità di gara → consumo di O₂ stimato (VO₂)
  • Durata della gara → % del VO₂max sostenibile
  • VDOT = VO₂ / %VO₂max

Valori di riferimento:  < 35 principiante · 35–45 amatoriale · 45–55 evoluto · 55–65 agonista · > 65 élite

─────────────────────────────────────────────
GRAFICO EVOLUZIONE VDOT
─────────────────────────────────────────────
Mostra come il tuo VDOT è cambiato nel tempo. La linea tratteggiata segna il tuo VDOT migliore storico. Un trend crescente indica miglioramento della forma fisica.

─────────────────────────────────────────────
TABELLA PREVISIONI
─────────────────────────────────────────────
Partendo dal tuo VDOT più recente (ultima gara), la formula inversa calcola il tempo atteso su 1K, 5K, 10K, mezza e maratona in condizioni ottimali.
Attenzione: le previsioni assumono allenamento specifico per quella distanza.

Fonte: Jack Daniels, "Daniels' Running Formula" (Human Kinetics).
Solo attività classificate come "Gara" su Strava (workout_type = 1) vengono incluse.""",
        "en": """\
## VDOT — Jack Daniels' Fitness Index

VDOT summarises your aerobic capacity derived directly from your actual race results, without laboratory tests.

─────────────────────────────────────────────
HOW IT IS CALCULATED
─────────────────────────────────────────────
Daniels' formula estimates the % of VO₂max sustainable in a race:
  • Race velocity → estimated O₂ consumption (VO₂)
  • Race duration → sustainable % of VO₂max
  • VDOT = VO₂ / %VO₂max

Reference values:  < 35 beginner · 35–45 recreational · 45–55 intermediate · 55–65 competitive · > 65 elite

─────────────────────────────────────────────
VDOT EVOLUTION CHART
─────────────────────────────────────────────
Shows how your VDOT has changed over time. The dashed line marks your all-time best. An upward trend indicates improving fitness.

─────────────────────────────────────────────
PREDICTIONS TABLE
─────────────────────────────────────────────
Based on your most recent VDOT (latest race), the inverse formula calculates expected times for 1K, 5K, 10K, half and full marathon under optimal conditions.
Note: predictions assume specific training for each distance.

Source: Jack Daniels, "Daniels' Running Formula" (Human Kinetics).
Only activities flagged as "Race" on Strava (workout_type = 1) are included.""",
        "de": """\
## VDOT — Jack Daniels' Leistungsindex

Der VDOT fasst Ihre aerobe Kapazität zusammen, abgeleitet aus echten Wettkampfergebnissen ohne Labortest.

BERECHNUNG: Daniels' Formel schätzt den nachhaltigen %VO₂max im Wettkampf.
  • VDOT = VO₂ / %VO₂max

Referenzwerte: < 35 Anfänger · 35–45 Hobbyläufer · 45–55 Fortgeschrittener · 55–65 Leistungsläufer · > 65 Elite

VDOT-ENTWICKLUNG: Zeigt die VDOT-Entwicklung im Zeitverlauf. Die gestrichelte Linie markiert den historischen Bestwert.

VORHERSAGETABELLE: Auf Basis des aktuellsten VDOT werden Zielzeiten für 1K, 5K, 10K, Halbmarathon und Marathon berechnet.

Quelle: Jack Daniels, "Daniels' Running Formula". Nur als "Wettkampf" markierte Aktivitäten (workout_type = 1) werden berücksichtigt.""",
        "fr": """\
## VDOT — Indice de forme de Jack Daniels

Le VDOT résume votre capacité aérobie à partir de vos résultats de course réels, sans test en laboratoire.

CALCUL : La formule de Daniels estime le %VO₂max soutenable en compétition.
  • VDOT = VO₂ / %VO₂max

Valeurs de référence : < 35 débutant · 35–45 loisir · 45–55 intermédiaire · 55–65 compétiteur · > 65 élite

GRAPHIQUE D'ÉVOLUTION : Montre l'évolution du VDOT dans le temps. La ligne pointillée marque le meilleur historique.

TABLEAU DE PRÉVISIONS : À partir du VDOT le plus récent, calcule les temps attendus sur 1K, 5K, 10K, semi et marathon.

Source : Jack Daniels, "Daniels' Running Formula". Seules les activités marquées "Course" sur Strava sont incluses.""",
        "es": """\
## VDOT — Índice de forma de Jack Daniels

El VDOT resume tu capacidad aeróbica a partir de resultados de carrera reales, sin pruebas de laboratorio.

CÁLCULO: La fórmula de Daniels estima el %VO₂máx sostenible en competición.
  • VDOT = VO₂ / %VO₂máx

Valores de referencia: < 35 principiante · 35–45 recreativo · 45–55 intermedio · 55–65 competidor · > 65 élite

GRÁFICO DE EVOLUCIÓN: Muestra la evolución del VDOT. La línea discontinua marca el mejor histórico.

TABLA DE PREDICCIONES: Basándose en el VDOT más reciente, calcula tiempos esperados para 1K, 5K, 10K, medio y maratón.

Fuente: Jack Daniels, "Daniels' Running Formula". Solo se incluyen actividades marcadas como "Carrera" en Strava.""",
    },

    "info_training_load": {
        "it": """\
## IL MODELLO PMC — Performance Management Chart

Questo grafico usa il modello di Banister (1991), adottato da TrainingPeaks, Garmin e WKO. Si basa sul TRIMP (TRaining IMPulse): durata × intensità cardiaca.

# CTL — FITNESS (linea blu)
Chronic Training Load: media esponenziale 42 giorni. Sale lentamente, scende lentamente. Un CTL alto = corpo adattato a grandi volumi.

# ATL — FATICA (linea rossa)
Acute Training Load: media esponenziale 7 giorni. Reagisce rapidamente alle sessioni intense.

# TSB — FORMA (linea verde)
Training Stress Balance = CTL − ATL.
• TSB positivo → riposato, pronto a gareggiare.
• TSB negativo → accumulo di fatica (normale in blocco di carico).
• TSB < −20 → rischio sovrallenamento.
• Sweet spot per gare: TSB tra +5 e +15.

NOTA DEL COACH: confronta i tuoi valori attuali con quelli di 3–12 mesi fa. Se CTL è più alto della stessa settimana dell'anno scorso, stai progredendo.""",
        "en": """\
## THE PMC MODEL — Performance Management Chart

This chart uses Banister's (1991) model, adopted by TrainingPeaks, Garmin and WKO. It is based on TRIMP (TRaining IMPulse): duration × cardiac intensity.

# CTL — FITNESS (blue line)
Chronic Training Load: 42-day exponential average. Rises and falls slowly. High CTL = body adapted to large volumes.

# ATL — FATIGUE (red line)
Acute Training Load: 7-day exponential average. Reacts quickly to intense sessions.

# TSB — FORM (green line)
Training Stress Balance = CTL − ATL.
• Positive TSB → rested, ready to race.
• Negative TSB → fatigue accumulation (normal during a training block).
• TSB < −20 → overtraining risk.
• Sweet spot for racing: TSB between +5 and +15.

COACH NOTE: compare your current values with those from 3–12 months ago. If CTL is higher than the same week last year, you are progressing.""",
        "de": """\
## DAS PMC-MODELL — Performance Management Chart

Dieses Diagramm verwendet Banisters (1991) Modell, eingesetzt von TrainingPeaks, Garmin und WKO. Basis: TRIMP = Dauer × Herzfrequenzintensität.

# CTL — FITNESS (blaue Linie)
Chronische Trainingsbelastung: 42-Tage-Exponentialmittel. Langsame Veränderung.

# ATL — ERSCHÖPFUNG (rote Linie)
Akute Trainingsbelastung: 7-Tage-Exponentialmittel. Reagiert schnell auf intensive Einheiten.

# TSB — FORM (grüne Linie)
TSB = CTL − ATL.
• Positiv → erholt, wettkampfbereit.
• Negativ → Erschöpfungsakkumulation (normal im Trainingsblock).
• TSB < −20 → Übertrainingsrisiko.
• Optimaler Bereich für Wettkämpfe: TSB +5 bis +15.""",
        "fr": """\
## LE MODÈLE PMC — Performance Management Chart

Ce graphique utilise le modèle de Banister (1991), adopté par TrainingPeaks, Garmin et WKO. Base : TRIMP = durée × intensité cardiaque.

# CTL — FORME (ligne bleue)
Charge d'entraînement chronique : moyenne exponentielle 42 jours. Évolue lentement.

# ATL — FATIGUE (ligne rouge)
Charge d'entraînement aiguë : moyenne exponentielle 7 jours. Réagit rapidement.

# TSB — CONDITION (ligne verte)
TSB = CTL − ATL.
• Positif → reposé, prêt à concourir.
• Négatif → accumulation de fatigue (normal en bloc de charge).
• TSB < −20 → risque de surentraînement.
• Zone idéale pour compétitions : TSB entre +5 et +15.""",
        "es": """\
## EL MODELO PMC — Performance Management Chart

Este gráfico usa el modelo de Banister (1991), adoptado por TrainingPeaks, Garmin y WKO. Base: TRIMP = duración × intensidad cardíaca.

# CTL — FORMA (línea azul)
Carga de entrenamiento crónica: media exponencial 42 días. Cambia lentamente.

# ATL — FATIGA (línea roja)
Carga de entrenamiento aguda: media exponencial 7 días. Reacciona rápidamente.

# TSB — CONDICIÓN (línea verde)
TSB = CTL − ATL.
• Positivo → descansado, listo para competir.
• Negativo → acumulación de fatiga (normal en bloque de carga).
• TSB < −20 → riesgo de sobreentrenamiento.
• Zona óptima para competiciones: TSB entre +5 y +15.""",
    },

    "info_grade": {
        "it": """\
## ANALISI PENDENZA — PACE vs GRADIENTE

Questo grafico mostra il tuo passo mediano (min/km) suddiviso per fasce di pendenza, calcolato dai tuoi split di 1 km. Viene anche usato dalla "Previsione Prestazioni" per la correzione dislivello personalizzata.

# FASCE DI PENDENZA
• < −8% Discesa ripida (blu scuro) — tecnica, rischio impatti
• −8 a −3% Discesa media (blu chiaro) — zona di recupero
• −3 a 0% Leggera discesa/piano (verde) — il tuo passo su asfalto
• 0 a 3% Piano/leggera salita (giallo) — fascia più comune su strada
• 3 a 8% Salita media (arancione) — sforzo aerobico significativo
• > 8% Salita ripida (rosso) — trail e cronoscalate

# COME USARLO
• Il differenziale piano→salita 3–8% indica i sec/km persi per ogni % di pendenza.
• Se discesa media è più lenta del piano: stai frenando — lavora su tecnica.

NOTA: questi dati alimentano la Previsione Prestazioni. Più split hai, più accurata è la stima.""",
        "en": """\
## GRADE ANALYSIS — PACE vs GRADIENT

This chart shows your median pace (min/km) broken down by gradient, calculated from your 1 km splits. It also feeds the "Performance Prediction" chart for personalised elevation correction.

# GRADIENT BANDS
• < −8% Steep downhill (dark blue) — technical, impact risk
• −8 to −3% Moderate downhill (light blue) — recovery zone
• −3 to 0% Gentle downhill/flat (green) — your road race pace
• 0 to 3% Flat/gentle uphill (yellow) — most common on roads
• 3 to 8% Moderate uphill (orange) — significant aerobic effort
• > 8% Steep uphill (red) — trail and hill climbs

# HOW TO USE IT
• The flat→uphill 3–8% pace differential shows sec/km lost per % of gradient.
• If moderate downhill is slower than flat: you're braking — work on technique.

NOTE: this data feeds the Performance Prediction. More splits = more accurate estimate.""",
        "de": """\
## STEIGUNGSANALYSE — TEMPO vs GRADIENT

Dieses Diagramm zeigt Ihr medianes Tempo (min/km) nach Steigungsbereichen, berechnet aus Ihren 1-km-Splits. Wird auch für die personalisierte Höhenkorrektur in der Leistungsvorhersage verwendet.

# STEIGUNGSBEREICHE
• < −8% Starkes Gefälle (dunkelblau) · −8 bis −3% Mittleres Gefälle (hellblau)
• −3 bis 0% Leichtes Gefälle/Flach (grün) · 0 bis 3% Flach/leichte Steigung (gelb)
• 3 bis 8% Mittlere Steigung (orange) · > 8% Starke Steigung (rot)

# ANWENDUNG
• Der Tempoverlust Flach→Steigung 3–8% zeigt Sek/km je % Steigung.
• Mittleres Gefälle langsamer als Flach = Sie bremsen — Technik verbessern.""",
        "fr": """\
## ANALYSE DE PENTE — ALLURE vs GRADIENT

Ce graphique montre votre allure médiane (min/km) par plage de pente, calculée à partir de vos fractions de 1 km. Alimente aussi la correction de dénivelé de la Prévision de performance.

# PLAGES DE PENTE
• < −8% Descente raide (bleu foncé) · −8 à −3% Descente modérée (bleu clair)
• −3 à 0% Légère descente/plat (vert) · 0 à 3% Plat/légère montée (jaune)
• 3 à 8% Montée modérée (orange) · > 8% Montée raide (rouge)

# UTILISATION
• L'écart d'allure plat→montée 3–8% indique les sec/km perdus par % de pente.
• Descente modérée plus lente que le plat = vous freinez — travaillez la technique.""",
        "es": """\
## ANÁLISIS DE PENDIENTE — RITMO vs GRADIENTE

Este gráfico muestra tu ritmo mediano (min/km) por rango de pendiente, calculado de tus parciales de 1 km. También alimenta la corrección de desnivel de la Predicción de rendimiento.

# RANGOS DE PENDIENTE
• < −8% Bajada pronunciada (azul oscuro) · −8 a −3% Bajada moderada (azul claro)
• −3 a 0% Bajada suave/llano (verde) · 0 a 3% Llano/subida suave (amarillo)
• 3 a 8% Subida moderada (naranja) · > 8% Subida pronunciada (rojo)

# CÓMO USARLO
• El diferencial llano→subida 3–8% indica seg/km perdidos por % de pendiente.
• Bajada moderada más lenta que llano = estás frenando — trabaja la técnica.""",
    },

    "info_perf_curve": {
        "it": """\
## CURVA DI PERFORMANCE — LEGGE POTENZA

Questo grafico mostra i tuoi migliori tempi su distanze standard (da 400m alla maratona) in piano log-log, con fit della curva t = A × d^b (legge di Riegel, 1977).

# IL MODELLO MATEMATICO
T = A × D^b · T = tempo (s) · D = distanza (m) · b = esponente di fatica

# L'ESPONENTE b — IL TUO PROFILO ATLETICO
• b < 1.03 → Velocista: più forte sulle corte, buona capacità anaerobica.
• b ≈ 1.03–1.06 → Bilanciato: profilo completo, simile ai runner élite.
• b > 1.06 → Fondista: più forte sulle lunghe, ottima efficienza aerobica.

# COME USARLO
• Punti sopra la curva = distanza non di forza.
• Punti sotto la curva = distanza di forza relativa.
• Curva che scende nel tempo = stai migliorando.
• b che si avvicina a 1.06 = stai diventando più completo.

NOTA DEL COACH: ricontrolla ogni 2–3 mesi. Se A diminuisce stai migliorando; se b si avvicina a 1.06 stai diventando più versatile.""",
        "en": """\
## PERFORMANCE CURVE — POWER LAW

This chart shows your best times for standard distances (400m to marathon) on a log-log plot, fitted with t = A × d^b (Riegel's law, 1977).

# THE MATHEMATICAL MODEL
T = A × D^b · T = time (s) · D = distance (m) · b = fatigue exponent

# THE EXPONENT b — YOUR ATHLETIC PROFILE
• b < 1.03 → Sprinter: stronger at short distances, good anaerobic capacity.
• b ≈ 1.03–1.06 → Balanced: versatile profile, similar to elite runners.
• b > 1.06 → Endurance: stronger at long distances, great aerobic efficiency.

# HOW TO USE IT
• Points above the curve = not your strength distance.
• Points below the curve = relative strength distance.
• Curve moving down over time = improving.
• b approaching 1.06 = becoming more versatile.

COACH NOTE: check every 2–3 months. If A decreases you're faster overall; if b approaches 1.06 you're becoming more complete.""",
        "de": """\
## LEISTUNGSKURVE — POTENZGESETZ

Zeigt Ihre Bestzeiten auf Standarddistanzen (400m bis Marathon) im log-log-Diagramm mit Fit t = A × d^b (Riegels Gesetz, 1977).

# DAS MODELL: T = A × D^b  ·  b = Ermüdungsexponent

# DER EXPONENT b — IHR ATHLETISCHES PROFIL
• b < 1.03 → Sprinter · b ≈ 1.03–1.06 → Ausgewogen · b > 1.06 → Ausdauerläufer

Punkte über der Kurve = nicht Ihre Stärkedistanz. Kurve fällt im Zeitverlauf = Verbesserung.""",
        "fr": """\
## COURBE DE PERFORMANCE — LOI PUISSANCE

Montre vos meilleurs temps sur distances standard (400m à marathon) en plan log-log, avec ajustement t = A × d^b (loi de Riegel, 1977).

# LE MODÈLE : T = A × D^b  ·  b = exposant de fatigue

# L'EXPOSANT b — VOTRE PROFIL ATHLÉTIQUE
• b < 1.03 → Sprinteur · b ≈ 1.03–1.06 → Équilibré · b > 1.06 → Fondeur

Points au-dessus de la courbe = distance pas dans vos points forts. Courbe qui descend = progression.""",
        "es": """\
## CURVA DE RENDIMIENTO — LEY DE POTENCIA

Muestra tus mejores tiempos en distancias estándar (400m a maratón) en escala log-log, con ajuste t = A × d^b (ley de Riegel, 1977).

# EL MODELO: T = A × D^b  ·  b = exponente de fatiga

# EL EXPONENTE b — TU PERFIL ATLÉTICO
• b < 1.03 → Velocista · b ≈ 1.03–1.06 → Equilibrado · b > 1.06 → Fondista

Puntos por encima de la curva = distancia no fuerte. Curva bajando = mejorando.""",
    },

    "info_race_pred": {
        "it": """\
## PREVISIONE PRESTAZIONI — SIMULAZIONE MONTE CARLO

Questo strumento stima il tuo tempo possibile su una distanza target, a partire dai tuoi best effort storici. Combina tre fasi: fit della curva di performance (Riegel), correzione personalizzata del dislivello, e simulazione Monte Carlo per quantificare l'incertezza.

---

# PARAMETRI DI INPUT

# Distanza
La distanza della gara da prevedere. Scegli tra le distanze standard (1 km, 5 km, 10 km, Mezza Maratona, Maratona) o seleziona "Personalizzata" per inserire qualsiasi valore.

# km personalizzati
Attivo solo con "Personalizzata". Inserisci la distanza in km (es. 8.5). Supporta decimali.

# Dislivello + (m)
Dislivello positivo totale del percorso obiettivo in metri. Lascia 0 per percorsi pianeggianti. La pendenza media viene calcolata come (dislivello_m / distanza_m) × 100 e usata per stimare il rallentamento. Trova questo valore nella scheda tecnica della gara.
• Esempi: 10K cittadino piatto → 0m. Mezza montagna → 400–800m. Trail KV → 1000m+

# Ultimi giorni
Finestra temporale dei best effort da considerare nel fit. 0 = tutto lo storico.
• 90 gg: forma attuale. Ideale se ti sei allenato in modo costante.
• 180–365 gg: stima stabile. Consigliato se hai pochi dati recenti.
• 0: massima copertura. Utile se hai poche gare o best effort registrati.
NOTA: se il filtro lascia meno di 2 distanze con dati, la previsione non può essere calcolata.

# km corsa min / max
Filtra i best effort in base alla lunghezza dell'attività che li contiene. Utile per considerare solo le corse simili per lunghezza alla gara obiettivo: se vuoi prevedere un 10K, impostare min=8 max=15 esclude best effort registrati durante maratone (paceati lentamente) o uscite brevissime.
• 0 = nessun limite (si considerano tutte le attività).

# Solo gare
Usa solo best effort da attività classificate come gara su Strava. Le gare rappresentano lo sforzo massimale e producono previsioni più accurate. Richiede che le attività siano state etichettate correttamente su Strava come "Gara".

---

# FASE 1 — FIT DELLA CURVA DI PERFORMANCE

Viene fittata la legge t = A × d^b sui tuoi migliori tempi di movimento (moving_time) per distanza, dopo aver applicato tutti i filtri impostati. Il pannello diagnostico in fondo al grafico mostra esattamente quali distanze e tempi vengono usati: verificare che siano coerenti con le tue prestazioni reali è il primo passo per valutare l'affidabilità della previsione.

---

# FASE 2 — CORREZIONE DISLIVELLO PERSONALIZZATA

Se il dislivello è > 0, il rallentamento viene stimato dai tuoi dati reali anziché da un modello fisso:
• Il grafico "Analisi Pendenza" calcola, tramite regressione lineare sui tuoi split di 1 km, quanti secondi/km perdi per ogni 1% di pendenza media.
• Questo coefficiente personale viene applicato alla pendenza media del percorso target.
• Se hai meno di 30 split su terreno variabile, si usa il modello empirico di Minetti come fallback (6 s/km per 1%).
• Il pannello diagnostico mostra quale fonte è stata usata e l'entità della correzione totale.

---

# FASE 3 — MONTE CARLO (5000 simulazioni)

Il tempo previsto non è un valore fisso: dipende dalla forma del giorno, dal meteo, dalla motivazione. Vengono generate 5000 simulazioni con rumore calibrato sui residui del fit (quanto i tuoi best effort si discostano dalla curva ideale). Il risultato è una distribuzione di tempi possibili.

---

# COME LEGGERE L'ISTOGRAMMA E I PERCENTILI

# P10 — Top / ottimistica
Solo il 10% delle simulazioni è più veloce. Potenziale massimo in condizioni ideali.

# P25 — Buona giornata
Il 25% delle simulazioni prevede un tempo migliore. Obiettivo ambizioso ma realistico.

# P50 — Stima mediana
Il tempo più probabile. 50% di probabilità di batterlo. Riferimento principale.

# P75 — Giornata normale
Il 75% delle simulazioni è più veloce. Raggiungibile anche senza condizioni eccezionali.

# P90 — Conservativa
Solo il 10% delle simulazioni è più lenta. Limite superiore utile per calibrare il ritmo di partenza in sicurezza.

---

# PANNELLO DIAGNOSTICO

In fondo al grafico trovi il riepilogo dei dati usati nel calcolo:
• Equazione del fit e confronto con b=1.060 (Riegel teorico)
• Tempo base grezzo prima delle correzioni
• Lista di ogni distanza usata con il tempo e il passo corrispondente
Verifica che questi tempi siano coerenti con le tue prestazioni: se un best effort è anomalo (es. una corsa lenta usata come 10K di riferimento), puoi escluderla usando i filtri "Ultimi giorni" o "km min/max".

---

# CONSIGLI PRATICI

• Parti al ritmo P50–P75 nei primi km. È meglio accelerare nel finale che esplodere.
• Se parti più veloce di P25, il rischio di crollo aumenta significativamente.
• Più best effort hai su distanze diverse, più il fit è preciso e l'incertezza si riduce.
• Per gare con molto dislivello, accumulare split su terreno simile nel grafico Analisi Pendenza migliora la correzione personalizzata.

---

NOTA DEL COACH: questo modello non conosce il tuo stato di forma attuale. Controlla il grafico CTL/TSB: se il TSB è positivo (+5 a +15) e il CTL è vicino al massimo storico, punta al P75. Se sei reduce da un blocco intenso o da riposo, punta al P25–P50.""",
        "en": """\
## PERFORMANCE PREDICTION — MONTE CARLO SIMULATION

This tool estimates your possible time for a target distance based on your historical best efforts. It combines three phases: performance curve fitting (Riegel), personalised elevation correction, and Monte Carlo simulation to quantify uncertainty.

---

# INPUT PARAMETERS

# Distance
The race distance to predict. Choose from standard distances (1 km, 5 km, 10 km, Half Marathon, Marathon) or select "Custom" to enter any value.

# Custom km
Active only with "Custom". Enter the distance in km (e.g. 8.5). Supports decimals.

# Elevation gain (m)
Total positive elevation gain of the target course in metres. Leave 0 for flat routes. Average gradient is calculated as (elevation_m / distance_m) × 100 and used to estimate slowdown. Find this value in the race's technical sheet.
• Examples: flat city 10K → 0m. Hilly half marathon → 400–800m. Vertical KM trail → 1000m+

# Last days
Time window for best efforts used in the fit. 0 = full history.
• 90 days: current form. Ideal if training has been consistent.
• 180–365 days: stable estimate. Recommended if recent data is sparse.
• 0: maximum coverage. Useful if you have few races or recorded best efforts.
NOTE: if the filter leaves fewer than 2 distances with data, the prediction cannot be calculated.

# Min / max run km
Filters best efforts by activity length. Useful to consider only runs similar in length to the target race: if predicting a 10K, setting min=8 max=15 excludes best efforts recorded during marathons (slow pace) or very short runs.
• 0 = no limit (all activities are considered).

# Races only
Use only best efforts from activities classified as a race on Strava. Races represent maximal effort and produce more accurate predictions. Requires activities to be correctly tagged as "Race" on Strava.

---

# PHASE 1 — PERFORMANCE CURVE FITTING

The law t = A × d^b is fitted to your best movement times (moving_time) per distance, after applying all set filters. The diagnostic panel at the bottom of the chart shows exactly which distances and times are used: verify that they match your actual performances — that is the first step in assessing the reliability of the prediction.

---

# PHASE 2 — PERSONALISED ELEVATION CORRECTION

If elevation gain is > 0, slowdown is estimated from your real data rather than a fixed model:
• The "Grade Analysis" chart calculates, via linear regression on your 1 km splits, how many seconds/km you lose per 1% of average gradient.
• This personal coefficient is applied to the average gradient of the target course.
• If you have fewer than 30 splits on variable terrain, Minetti's empirical model is used as a fallback (6 s/km per 1%).
• The diagnostic panel shows which source was used and the total correction applied.

---

# PHASE 3 — MONTE CARLO (5000 simulations)

The predicted time is not a fixed value: it depends on day form, weather, motivation. 5000 simulations are generated with noise calibrated on the fit residuals (how much your best efforts deviate from the ideal curve). The result is a distribution of possible times.

---

# HOW TO READ THE HISTOGRAM AND PERCENTILES

# P10 — Top / optimistic
Only 10% of simulations are faster. Maximum potential under ideal conditions.

# P25 — Good day
25% of simulations predict a better time. An ambitious but realistic goal.

# P50 — Median estimate
The most likely time. 50% probability of beating it. Main reference point.

# P75 — Normal day
75% of simulations are faster. Achievable even without exceptional conditions.

# P90 — Conservative
Only 10% of simulations are slower. A useful upper bound for calibrating a safe starting pace.

---

# DIAGNOSTIC PANEL

At the bottom of the chart you find a summary of the data used:
• Fit equation and comparison with b=1.060 (theoretical Riegel)
• Raw base time before corrections
• List of each distance used with corresponding time and pace
Verify that these times match your actual performances: if a best effort is an outlier (e.g. a slow run used as a 10K reference), you can exclude it using the "Last days" or "km min/max" filters.

---

# PRACTICAL TIPS

• Start at P50–P75 pace in the first km. It is better to accelerate at the finish than to blow up.
• Starting faster than P25 significantly increases the risk of a late-race collapse.
• The more best efforts you have across different distances, the more precise the fit and the lower the uncertainty.
• For races with significant elevation, accumulating splits on similar terrain in the Grade Analysis chart improves the personalised correction.

---

COACH NOTE: this model does not know your current fitness state. Check the CTL/TSB chart: if TSB is positive (+5 to +15) and CTL is close to your historical peak, aim for P75. If you are coming off an intense block or rest period, aim for P25–P50.""",
        "de": """\
## LEISTUNGSVORHERSAGE — MONTE-CARLO-SIMULATION

Dieses Tool schätzt Ihre mögliche Zeit für eine Zieldistanz auf Basis Ihrer historischen Bestleistungen. Es kombiniert drei Phasen: Kurvenanpassung (Riegel), personalisierte Höhenkorrektur und Monte-Carlo-Simulation zur Quantifizierung der Unsicherheit.

---

# EINGABEPARAMETER

# Distanz
Die vorherzusagende Wettkampfdistanz. Wählen Sie aus Standarddistanzen (1 km, 5 km, 10 km, Halbmarathon, Marathon) oder wählen Sie "Benutzerdefiniert".

# Benutzerdefinierte km
Nur bei "Benutzerdefiniert" aktiv. Geben Sie die Distanz in km ein (z. B. 8.5). Dezimalzahlen werden unterstützt.

# Höhengewinn (m)
Gesamter positiver Höhenunterschied der Zielstrecke in Metern. 0 für flache Strecken. Das mittlere Gefälle wird als (Höhe_m / Distanz_m) × 100 berechnet. Den Wert finden Sie in den technischen Daten des Wettkampfs.
• Beispiele: flacher Stadtkurs 10K → 0m. Hügeliger Halbmarathon → 400–800m. Trail KV → 1000m+

# Letzte Tage
Zeitfenster der in den Fit einbezogenen Bestleistungen. 0 = vollständige Historie.
• 90 Tage: aktuelle Form. Ideal bei gleichmäßigem Training.
• 180–365 Tage: stabile Schätzung. Empfohlen bei wenigen aktuellen Daten.
• 0: maximale Abdeckung. Sinnvoll bei wenigen Wettkämpfen.
HINWEIS: Bleiben nach dem Filter weniger als 2 Distanzen übrig, kann keine Vorhersage berechnet werden.

# Min / Max Laufkm
Filtert Bestleistungen nach Aktivitätslänge. Nützlich, um nur Läufe ähnlicher Länge zur Zieldistanz zu berücksichtigen.
• 0 = kein Limit.

# Nur Wettkämpfe
Nur Bestleistungen aus als Wettkampf eingestuften Aktivitäten. Wettkämpfe spiegeln maximale Anstrengung wider und liefern genauere Vorhersagen.

---

# PHASE 1 — KURVENANPASSUNG

Das Gesetz t = A × d^b wird an Ihre besten Bewegungszeiten angepasst. Das Diagnose-Panel zeigt genau, welche Distanzen und Zeiten verwendet wurden.

---

# PHASE 2 — PERSONALISIERTE HÖHENKORREKTUR

Bei Höhengewinn > 0 wird die Verlangsamung aus Ihren echten Daten geschätzt:
• Das „Steigungsanalyse"-Diagramm berechnet per linearer Regression, wie viele Sek./km Sie pro 1% mittlerem Gefälle verlieren.
• Bei weniger als 30 Splits wird Minettis empirisches Modell verwendet (6 s/km je 1%).
• Das Diagnose-Panel zeigt, welche Quelle verwendet wurde und die Gesamtkorrektur.

---

# PHASE 3 — MONTE CARLO (5000 Simulationen)

5000 Simulationen werden mit kalibriertem Rauschen auf Basis der Fit-Residuen generiert. Das Ergebnis ist eine Verteilung möglicher Zeiten.

---

# HISTOGRAMM UND PERZENTILE

# P10 — Optimal / optimistisch
Nur 10% der Simulationen sind schneller. Maximales Potenzial unter idealen Bedingungen.

# P25 — Guter Tag
25% der Simulationen prognostizieren eine bessere Zeit. Ambitioniertes, realistisches Ziel.

# P50 — Median-Schätzung
Die wahrscheinlichste Zeit. 50% Wahrscheinlichkeit, sie zu unterbieten. Hauptreferenz.

# P75 — Normaler Tag
75% der Simulationen sind schneller. Auch ohne Ausnahmeform erreichbar.

# P90 — Konservativ
Nur 10% der Simulationen sind langsamer. Obere Grenze für sichere Starttempoplanung.

---

# DIAGNOSE-PANEL

• Fit-Gleichung und Vergleich mit b=1.060 (theoretischer Riegel)
• Rohe Basiszeit vor Korrekturen
• Liste jeder verwendeten Distanz mit Zeit und Tempo

---

# PRAKTISCHE TIPPS

• Starten Sie in den ersten km im P50–P75-Tempo. Besser im Finish beschleunigen als früh einbrechen.
• Start schneller als P25 erhöht das Einbruchsrisiko erheblich.
• Mehr Bestleistungen auf verschiedenen Distanzen = präziserer Fit und geringere Unsicherheit.
• Bei Wettkämpfen mit viel Höhenunterschied verbessern mehr Splits auf ähnlichem Terrain die personalisierte Korrektur.

---

TRAINER-HINWEIS: dieses Modell kennt Ihren aktuellen Fitnesszustand nicht. Prüfen Sie den CTL/TSB-Graphen: bei positivem TSB (+5 bis +15) und hohem CTL → P75 anpeilen. Nach intensivem Block oder Erholung → P25–P50.""",
        "fr": """\
## PRÉVISION DE PERFORMANCE — SIMULATION MONTE CARLO

Cet outil estime votre temps possible sur une distance cible à partir de vos meilleurs efforts historiques. Il combine trois phases : ajustement de la courbe de performance (Riegel), correction personnalisée du dénivelé et simulation Monte Carlo pour quantifier l'incertitude.

---

# PARAMÈTRES D'ENTRÉE

# Distance
La distance de course à prévoir. Choisissez parmi les distances standard (1 km, 5 km, 10 km, Semi-marathon, Marathon) ou sélectionnez "Personnalisée".

# km personnalisés
Actif uniquement avec "Personnalisée". Saisissez la distance en km (ex. 8.5). Accepte les décimales.

# Dénivelé + (m)
Dénivelé positif total du parcours cible en mètres. Laissez 0 pour les parcours plats. La pente moyenne est calculée comme (dénivelé_m / distance_m) × 100. Trouvez cette valeur dans la fiche technique de la course.
• Exemples : 10K citadin plat → 0m. Semi de montagne → 400–800m. Trail KV → 1000m+

# Derniers jours
Fenêtre temporelle des meilleurs efforts à considérer. 0 = tout l'historique.
• 90 j : forme actuelle. Idéal si l'entraînement est régulier.
• 180–365 j : estimation stable. Conseillé si les données récentes sont rares.
• 0 : couverture maximale. Utile si peu de courses enregistrées.
REMARQUE : si le filtre laisse moins de 2 distances avec données, la prévision ne peut pas être calculée.

# km course min / max
Filtre les meilleurs efforts selon la longueur de l'activité. Utile pour ne considérer que les courses de longueur similaire à la course cible.
• 0 = pas de limite.

# Courses uniquement
Utilise uniquement les meilleurs efforts d'activités classées comme course sur Strava. Les courses représentent l'effort maximal et produisent des prévisions plus précises.

---

# PHASE 1 — AJUSTEMENT DE LA COURBE

La loi t = A × d^b est ajustée sur vos meilleurs temps de déplacement après application des filtres. Le panneau de diagnostic montre exactement quelles distances et temps sont utilisés.

---

# PHASE 2 — CORRECTION DE DÉNIVELÉ PERSONNALISÉE

Si dénivelé > 0, le ralentissement est estimé à partir de vos données réelles :
• Le graphique « Analyse de pente » calcule, via régression linéaire sur vos fractions de 1 km, combien de sec/km vous perdez par 1% de pente.
• Ce coefficient personnel est appliqué à la pente moyenne du parcours cible.
• Si moins de 30 fractions sur terrain varié, le modèle empirique de Minetti est utilisé (6 s/km par 1%).
• Le panneau de diagnostic indique quelle source a été utilisée et l'ampleur de la correction.

---

# PHASE 3 — MONTE CARLO (5000 simulations)

5000 simulations sont générées avec un bruit calibré sur les résidus du fit. Le résultat est une distribution de temps possibles.

---

# LIRE L'HISTOGRAMME ET LES PERCENTILES

# P10 — Top / optimiste
Seules 10% des simulations sont plus rapides. Potentiel maximum dans des conditions idéales.

# P25 — Bonne journée
25% des simulations prévoient un meilleur temps. Objectif ambitieux mais réaliste.

# P50 — Estimation médiane
Le temps le plus probable. 50% de probabilité de le battre. Référence principale.

# P75 — Journée normale
75% des simulations sont plus rapides. Atteignable même sans conditions exceptionnelles.

# P90 — Conservatrice
Seules 10% des simulations sont plus lentes. Borne supérieure pour calibrer l'allure de départ en sécurité.

---

# PANNEAU DE DIAGNOSTIC

• Équation du fit et comparaison avec b=1.060 (Riegel théorique)
• Temps de base brut avant corrections
• Liste de chaque distance utilisée avec le temps et l'allure correspondants
Vérifiez que ces temps correspondent à vos performances réelles : si un effort est aberrant, utilisez les filtres "Derniers jours" ou "km min/max".

---

# CONSEILS PRATIQUES

• Partez à l'allure P50–P75 dans les premiers km. Mieux vaut accélérer en fin de course que s'effondrer.
• Partir plus vite que P25 augmente significativement le risque d'effondrement.
• Plus vous avez de meilleurs efforts sur différentes distances, plus le fit est précis.
• Pour les courses avec beaucoup de dénivelé, accumuler des fractions sur terrain similaire améliore la correction personnalisée.

---

NOTE DU COACH : ce modèle ne connaît pas votre état de forme actuel. Vérifiez le graphique CTL/TSB : si le TSB est positif (+5 à +15) et le CTL proche du maximum historique, visez le P75. Si vous sortez d'un bloc intensif ou d'une période de repos, visez le P25–P50.""",
        "es": """\
## PREDICCIÓN DE RENDIMIENTO — SIMULACIÓN MONTE CARLO

Esta herramienta estima tu tiempo posible en una distancia objetivo a partir de tus mejores esfuerzos históricos. Combina tres fases: ajuste de la curva de rendimiento (Riegel), corrección personalizada del desnivel y simulación Monte Carlo para cuantificar la incertidumbre.

---

# PARÁMETROS DE ENTRADA

# Distancia
La distancia de carrera a predecir. Elige entre las distancias estándar (1 km, 5 km, 10 km, Media Maratón, Maratón) o selecciona "Personalizada".

# km personalizados
Activo solo con "Personalizada". Introduce la distancia en km (ej. 8.5). Admite decimales.

# Desnivel + (m)
Desnivel positivo total del recorrido objetivo en metros. Deja 0 para recorridos llanos. La pendiente media se calcula como (desnivel_m / distancia_m) × 100. Encuentra este valor en la ficha técnica de la carrera.
• Ejemplos: 10K urbano llano → 0m. Media montaña → 400–800m. Trail KV → 1000m+

# Últimos días
Ventana temporal de los mejores esfuerzos a considerar en el ajuste. 0 = todo el historial.
• 90 días: forma actual. Ideal si el entrenamiento ha sido constante.
• 180–365 días: estimación estable. Recomendado si los datos recientes son escasos.
• 0: cobertura máxima. Útil si tienes pocas carreras registradas.
NOTA: si el filtro deja menos de 2 distancias con datos, la predicción no puede calcularse.

# km carrera mín / máx
Filtra los mejores esfuerzos según la longitud de la actividad. Útil para considerar solo las carreras de longitud similar a la carrera objetivo.
• 0 = sin límite.

# Solo carreras
Usa solo mejores esfuerzos de actividades clasificadas como carrera en Strava. Las carreras representan el esfuerzo máximo y producen predicciones más precisas.

---

# FASE 1 — AJUSTE DE LA CURVA DE RENDIMIENTO

Se ajusta la ley t = A × d^b a tus mejores tiempos de movimiento después de aplicar todos los filtros. El panel de diagnóstico muestra exactamente qué distancias y tiempos se utilizan.

---

# FASE 2 — CORRECCIÓN DE DESNIVEL PERSONALIZADA

Si el desnivel es > 0, la ralentización se estima a partir de tus datos reales:
• El gráfico "Análisis de Pendiente" calcula, mediante regresión lineal sobre tus parciales de 1 km, cuántos segundos/km pierdes por cada 1% de pendiente media.
• Este coeficiente personal se aplica a la pendiente media del recorrido objetivo.
• Si tienes menos de 30 parciales en terreno variable, se usa el modelo empírico de Minetti (6 s/km por 1%).
• El panel de diagnóstico muestra qué fuente se usó y la magnitud de la corrección total.

---

# FASE 3 — MONTE CARLO (5000 simulaciones)

Se generan 5000 simulaciones con ruido calibrado sobre los residuos del ajuste. El resultado es una distribución de tiempos posibles.

---

# CÓMO LEER EL HISTOGRAMA Y LOS PERCENTILES

# P10 — Top / optimista
Solo el 10% de las simulaciones es más rápido. Potencial máximo en condiciones ideales.

# P25 — Buen día
El 25% de las simulaciones predice un tiempo mejor. Objetivo ambicioso pero realista.

# P50 — Estimación mediana
El tiempo más probable. 50% de probabilidad de superarlo. Referencia principal.

# P75 — Día normal
El 75% de las simulaciones es más rápido. Alcanzable incluso sin condiciones excepcionales.

# P90 — Conservadora
Solo el 10% de las simulaciones es más lento. Límite superior para calibrar el ritmo de salida con seguridad.

---

# PANEL DE DIAGNÓSTICO

• Ecuación del ajuste y comparación con b=1.060 (Riegel teórico)
• Tiempo base bruto antes de las correcciones
• Lista de cada distancia utilizada con el tiempo y el ritmo correspondientes
Verifica que estos tiempos correspondan a tus prestaciones reales: si un mejor esfuerzo es anómalo, puedes excluirlo con los filtros "Últimos días" o "km mín/máx".

---

# CONSEJOS PRÁCTICOS

• Sal al ritmo P50–P75 en los primeros km. Es mejor acelerar al final que explotar.
• Salir más rápido que P25 aumenta significativamente el riesgo de colapso.
• Cuantos más mejores esfuerzos tengas en distintas distancias, más preciso será el ajuste.
• Para carreras con mucho desnivel, acumular parciales en terreno similar mejora la corrección personalizada.

---

NOTA DEL ENTRENADOR: este modelo no conoce tu estado de forma actual. Consulta el gráfico CTL/TSB: si el TSB es positivo (+5 a +15) y el CTL está cerca del máximo histórico, apunta al P75. Si vienes de un bloque intenso o descanso, apunta al P25–P50.""",
    },

    # ── Info / help panel in widgets ──────────────────────────────────────────
    "btn_info":              {"it": "ℹ  Info",    "en": "ℹ  Info",    "de": "ℹ  Info",    "fr": "ℹ  Info",    "es": "ℹ  Info"},
    "btn_info_close":        {"it": "✕  Chiudi",  "en": "✕  Close",   "de": "✕  Schließen","fr": "✕  Fermer",  "es": "✕  Cerrar"},

    # ── Error labels ──────────────────────────────────────────────────────────
    "install_matplotlib":    {"it": "Installa matplotlib:  pip install matplotlib", "en": "Install matplotlib:  pip install matplotlib", "de": "Matplotlib installieren:  pip install matplotlib", "fr": "Installez matplotlib :  pip install matplotlib", "es": "Instala matplotlib:  pip install matplotlib"},
    "error_loading_data":    {"it": "Errore caricamento dati:",  "en": "Error loading data:",   "de": "Fehler beim Laden der Daten:", "fr": "Erreur de chargement :", "es": "Error al cargar datos:"},
    "no_runs_library":       {"it": "Nessuna corsa in libreria.\n\nScarica o importa delle attività prima.", "en": "No runs in library.\n\nDownload or import activities first.", "de": "Keine Läufe in der Bibliothek.\n\nLade oder importiere Aktivitäten zuerst.", "fr": "Aucune sortie dans la bibliothèque.\n\nTéléchargez ou importez des activités d'abord.", "es": "No hay carreras en la biblioteca.\n\nDescarga o importa actividades primero."},
    "heatmap_win_title":     {"it": "Heatmap — caricamento…",   "en": "Heatmap — loading…",    "de": "Heatmap — wird geladen…",     "fr": "Carte de chaleur — chargement…","es": "Mapa de calor — cargando…"},

    # ── Donation button ───────────────────────────────────────────────────────
    "donate_label":          {"it": "☕  Offrimi un caffè",      "en": "☕  Buy me a coffee",    "de": "☕  Kauf mir einen Kaffee",   "fr": "☕  Offre-moi un café",       "es": "☕  Invítame un café"},
    "donate_sub":            {"it": "ogni km conta  🧡",         "en": "every km counts  🧡",    "de": "jeder km zählt  🧡",          "fr": "chaque km compte  🧡",        "es": "cada km cuenta  🧡"},
    "tooltip_donate":        {"it": "Sostieni il progetto con una donazione PayPal — nessuna pressione, ogni contributo è benvenuto!", "en": "Support the project with a PayPal donation — no pressure, every contribution is welcome!", "de": "Unterstütze das Projekt mit einer PayPal-Spende — kein Druck, jeder Beitrag ist willkommen!", "fr": "Soutenez le projet avec un don PayPal — sans pression, toute contribution est bienvenue !", "es": "Apoya el proyecto con una donación PayPal — sin presión, ¡toda contribución es bienvenida!"},
}


def t(key: str) -> str:
    """Return translated string for the active language.

    Falls back to Italian, then to the key itself.
    """
    entry = _TRANSLATIONS.get(key)
    if entry is None:
        return key
    # For list-valued keys (days_short, months_short, etc.) return as-is
    val = entry.get(_active_lang)
    if val is None:
        val = entry.get("it", key)
    return val  # type: ignore[return-value]


def set_language(lang: str) -> None:
    global _active_lang
    if lang in SUPPORTED_LANGUAGES:
        _active_lang = lang


def get_language() -> str:
    return _active_lang
