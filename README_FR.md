# ⬡ Strava Viewer 3.0

Application de bureau pour analyser, visualiser et comparer les activités de course téléchargées depuis Strava. Interface graphique native (tkinter), thème clair/sombre et MongoDB comme unique backend de stockage.

---

> Si ce projet vous est utile et que vous souhaitez offrir un café virtuel au développeur, vous pouvez le faire ici → [☕ PayPal](https://paypal.me/TeoVr81). Sans pression — chaque km compte, donation ou non.

---

## Fonctionnalités

### Ouverture des activités
- Téléchargez directement toutes vos courses depuis Strava avec le bouton **Télécharger depuis Strava** — les activités sont sauvegardées sur MongoDB

### Tableau de bord
Vue d'ensemble complète de l'activité ouverte :
- Distance, temps actif/total, allure moyenne et meilleure, vitesse
- Dénivelé positif et négatif
- Fréquence cardiaque moyenne et maximale, cadence, calories
- Indices de performance (Suffer Score, VAM, etc.)

### Graphiques
Cinq graphiques intégrés dans l'interface :
- **Allure par km** — barres colorées (vert = plus rapide que la moyenne, bleu = dans la moyenne, rouge = plus lent)
- **Vitesse** — ligne avec zone remplie
- **Dénivelé** — graphique en barres
- **Fréquence cardiaque** — série temporelle
- **Cadence** — tendance par kilomètre

### Zones FC
- Réglage manuel de la fréquence cardiaque maximale
- Distribution du temps par zone (Z1–Z5) avec barres horizontales colorées
- Graphique de dispersion FC vs allure avec ligne de tendance et bandes de zone

### Carte GPS
La carte s'ouvre dans le **navigateur par défaut** (Chrome, Edge, Firefox…) et comprend :

- **Sélecteur de couche** — quatre fonds sélectionnables depuis le panneau en haut à droite :
  - *Sombre* (CartoDB dark matter, défaut)
  - *OpenStreetMap*
  - *Satellite* (Esri WorldImagery, vraies images satellites, sans clé API)
  - *Clair* (CartoDB positron)
- **Tracé coloré par allure** — la polyligne est découpée km par km avec un dégradé vert → jaune → rouge (vert = km le plus rapide, rouge = km le plus lent) ; en passant la souris sur chaque segment apparaît l'info-bulle avec l'allure, la FC et le dénivelé du km
- **Marqueurs kilométriques** — un indicateur numéroté pour chaque km complété ; en cliquant s'ouvre une fenêtre contextuelle avec l'allure, la FC moyenne et le dénivelé de ce kilomètre
- **Fenêtres contextuelles Départ/Fin enrichies** — marqueur vert (départ) et rouge (fin) avec fenêtres complètes : date, distance, temps, allure moyenne/maximale, FC, dénivelé, calories, Suffer Score
- **Superposition de statistiques** — barre fixe en haut de la carte avec les métriques clés de l'activité (nom, distance, temps, allure, FC, dénivelé)
- **Bouton Plein écran** — étend la carte en plein écran dans le navigateur
- **MiniCarte** — carte panoramique 150×150 dans le coin inférieur droit pour s'orienter lors du zoom ; activable/désactivable

Nécessite la permission Strava `activity:read_all` pour la polyligne GPS et une connexion internet pour charger les tuiles dans le navigateur.

### Splits
Tableau déroulant avec les données kilomètre par kilomètre :
- Distance, temps, allure, vitesse, FC, dénivelé, cadence
- Couleur de l'allure pour identifier immédiatement les km les plus rapides/lents

### Détection d'intervalles *(nouveau)*
Détection automatique et analyse des séances d'entraînement par intervalles structurés à partir des données de splits par km :
- **Détection automatique** — l'algorithme calcule la moyenne et l'écart-type de l'allure et classe chaque km comme *rapide*, *lent* ou *neutre* avec un seuil ±0,5σ ; nécessite au moins 3 segments rapides et un coefficient de variation ≥ 6%
- **Classification de l'entraînement** — identifie automatiquement le type de séance : *Intervalles VO₂max*, *Intervalles au seuil*, *Tempo / Progressif*, *Fartlek*, *Foulées légères*
- **Bande d'analyse** — 4 StatCards : allure travail moyenne, allure récupération moyenne, taux de déclin (dernier vs premier intervalle), score de régularité (0–100)
- **Tableau des segments** — liste déroulante de tous les segments détectés avec type (⚡ Travail / ○ Récupération), distance, temps, allure, FC et delta vs moyenne ; les intervalles de travail sont mis en évidence avec une bordure gauche orange
- **Graphiques** — graphique en barres de l'allure par segment (orange = travail, bleu = récupération) avec lignes de référence ; graphique linéaire de la FC par segment si disponible
- Pour les séances non-intervalles, affiche un message clair « Pas une séance d'intervalles » avec les statistiques d'uniformité d'allure

### Meilleures performances
Liste des meilleures performances détectées par Strava (1 km, 5 km, 10 km, semi-marathon, marathon, etc.) avec badge 🏆 pour les records personnels.

### Comparaison
Comparaison côte à côte de jusqu'à 5 activités :
- Tableau comparatif avec mise en évidence verte (meilleur) et rouge (pire) pour chaque métrique
- Graphique d'allure km par km superposé
- Graphique de fréquence cardiaque superposé
- Ajout d'activités depuis l'onglet Bibliothèque avec le bouton ➕

### Bibliothèque
Liste de toutes les courses sauvegardées dans la base de données, avec :
- **Pagination** — 100 lignes par page avec navigation ◀ ▶
- **Filtres** par nom/description, distance (min–max km), plage de dates, et **Courses seulement** (filtre les activités avec `workout_type = race`)
- Couleur d'allure **sémantique** : vert < 5:00/km, jaune < 6:30/km, rouge au-delà
- Survol de ligne avec mise en évidence visuelle
- Ouverture d'activité avec 📂, ajout à la comparaison avec ➕, suppression avec 🗑
- Indicateur de l'état de la connexion MongoDB

### Calendrier
Vue mensuelle de toutes les courses avec navigation mois par mois :
- Chaque cellule avec une course affiche la distance, l'allure et la fréquence cardiaque ; l'intensité de la couleur orange est **proportionnelle aux km parcourus** par rapport au jour le plus long du mois (carte de chaleur)
- Les jours avec plusieurs courses affichent un compteur supplémentaire avec des boutons ◀ ▶ pour faire défiler les courses du même jour
- Boutons ◀ ▶ pour naviguer entre les mois, "Aujourd'hui" pour revenir au mois en cours
- Cliquer sur une cellule ouvre l'activité dans l'onglet Tableau de bord
- Le total km et le nombre de courses du mois est affiché dans l'en-tête

### Statistiques
Statistiques agrégées sur **toutes** les courses dans la base de données (ignore les filtres et la pagination) :
- **Objectif annuel** — définissez un objectif km pour l'année en cours avec barre de progression ; la valeur est sauvegardée dans MongoDB et mémorisée entre les sessions
- Totaux : courses, km, heures, dénivelé, allure moyenne, FC moyenne, calories, km/semaine
- **Carte de chaleur des activités** — grille calendrier style GitHub des 52 dernières semaines (lignes = jours de la semaine Lun→Dim, colonnes = semaines) : chaque cellule est colorée en orange avec une intensité proportionnelle aux km courus ce jour-là, gris foncé si repos ; barre d'échelle de couleur en bas ; info-bulle au survol avec date et km
- **Profil athlétique** — graphique radar hexagonal avec 6 dimensions normalisées 0–100 : *Vitesse* (allure moyenne, échelle 8:20→3:20/km), *Endurance* (médiane des distances, échelle 3→42 km), *Dénivelé* (moyenne m↑/km, échelle 0→40 m/km), *Constance* (% semaines avec au moins une course dans les 52 dernières), *Volume* (moyenne km/semaine dans les 52 dernières, échelle 0→70), *Progression* (comparaison de l'allure moyenne des 3 derniers mois vs les 3 mois précédents) ; accompagné d'un panneau avec scores numériques, barres proportionnelles et description de chaque dimension
- **Tableau mensuel** — 12 derniers mois avec km, courses, temps, allure moyenne, dénivelé ; graphique à barres km par mois
- Tableau annuel avec km, courses, temps, allure moyenne, dénivelé ; graphique km par an et courses par an
- Distribution des distances (camembert)
- **Charge d'entraînement** — graphique ATL/CTL/TSB (Banister TRIMP) des 12 derniers mois :
  - *CTL (Forme)* — moyenne pondérée exponentielle sur 42 jours
  - *ATL (Fatigue)* — moyenne pondérée exponentielle sur 7 jours
  - *TSB (État de forme)* — CTL − ATL (positif = reposé, négatif = fatigué)
- **Records personnels** — tableau avec le meilleur temps personnel pour les distances canoniques (1 km, 5 km, 10 km, Semi-Marathon, Marathon), avec le nom de l'activité et la date de réalisation
- **Analyse de pente (Grade Analysis)** — graphique à barres de l'allure médiane répartie par 6 bandes de gradient (de la descente raide <−8% à la montée >8%), calculé à partir des splits de 1 km enregistrés par Strava ; filtres "Derniers jours" et "Courses seulement" ; les données de ce graphique alimentent la correction de dénivelé personnalisée de la Prévision de Performance ; bouton ℹ avec guide par bande et conseils d'entraînement
- **Courbe de performance** — graphique log-log distance vs temps sur les meilleures performances (de 400m au marathon) avec ajustement de la loi de puissance `t = A × d^b` ; les temps utilisés sont le `moving_time` (pauses exclues) ; filtres "Derniers jours" et "Courses seulement" ; l'exposant `b` révèle le profil athlétique (sprinter vs fondeur, comparaison avec b=1.06 de Riegel) ; bouton ℹ avec théorie et guide d'interprétation
- **Prévision de performance (Monte Carlo)** — estimation du temps sur n'importe quelle distance avec simulation de 5000 scénarios ; paramètres configurables : distance cible (standard ou personnalisée en km), dénivelé positif du parcours, fenêtre temporelle de l'historique (N derniers jours), longueur minimale et maximale des courses pour récupérer les meilleures performances (km min/max), filtre courses seulement ; la correction de dénivelé est personnalisée : calculée par régression linéaire sur vos vrais splits (sec/km par 1% de pente), avec recours au modèle Minetti si les données sont insuffisantes ; le résultat est un histogramme avec les percentiles P10/P25/P50/P75/P90 et un panneau de diagnostic avec les données utilisées dans l'ajustement, le coefficient b et le temps de base brut ; bouton ℹ avec guide complet sur les paramètres, le calcul et l'interprétation des résultats
- **Analyse des courses et VDOT** — analyse toutes les activités classées comme "Course" sur Strava (`workout_type = 1`) et calcule pour chacune le VDOT selon la formule de Jack Daniels (indice de capacité aérobie dérivé de la distance et du temps réels, sans test en laboratoire) ; affiche trois cartes de statistiques (total des courses, meilleur VDOT, VDOT le plus récent), un graphique linéaire de l'évolution du VDOT dans le temps avec ligne pointillée au maximum historique, un tableau de courses paginé (10 par page, cliquable pour ouvrir l'activité) avec date, km, temps, VDOT et nom, et un tableau de prévisions pour 1K / 5K / 10K / semi-marathon / marathon calculées à partir du VDOT de la dernière course enregistrée ; bouton ℹ avec explication de la formule, tableau de valeurs de référence (débutant → élite) et guide d'interprétation des prévisions
- **Parcours récurrents** — détecte automatiquement les parcours que vous avez courus au moins 3 fois en regroupant les activités par zone de départ (~300 m) et distance (±1 km) ; pour chaque groupe affiche : liste déroulante avec le nom le plus fréquent, distance, nombre de courses, période et ville/coordonnées ; graphique de dispersion de l'allure dans le temps avec colorisation vert→rouge (plus rapide→plus lent), ligne de tendance pointillée, mise en évidence de la meilleure course et de la dernière ; en-tête avec meilleure allure, allure moyenne et indicateur de tendance (amélioré/dégradé/stable) ; liste des courses du groupe avec date, km, allure, FC et nom, cliquable pour ouvrir l'activité ; la ville est récupérée d'abord depuis les métadonnées Strava, puis via le géocodage inverse Nominatim (OpenStreetMap) avec cache persistant sur MongoDB, fil séquentiel avec pause de 1 seconde entre les requêtes pour respecter les limites de débit

### Suivi d'équipement / chaussures *(nouveau)*
Agrégation automatique du kilométrage par chaussure/équipement défini sur Strava :
- **Cartes par équipement** — une carte par chaussure avec : km totaux, nombre de sorties, allure moyenne, dates de première/dernière utilisation
- **Barre de progression** — remplissage visuel vers un seuil de remplacement configurable par chaussure (700 km par défaut)
- **Badge de statut** — ✓ OK (< 80%), → Près de la limite (80–100%), ⚠ À remplacer bientôt (> 100%)
- **Seuil modifiable** — champ texte et bouton Enregistrer par chaussure ; valeur persistée dans MongoDB
- **Graphique km mensuels** — graphique à barres empilées des 12 derniers mois, une couleur par gear
- Les données d'équipement proviennent des téléchargements Strava ; si aucun gear n'est assigné, un message d'état vide est affiché

### Base de données
Depuis le menu **Base de données** dans la barre supérieure :
- **Exporter ZIP** — exporte toutes les activités de la base de données dans une archive `.zip` (un fichier JSON par course) ; utile comme sauvegarde ou pour déplacer la base de données vers une autre machine
- **Importer ZIP** — importe une archive `.zip` précédemment exportée ; les activités déjà présentes sont ignorées (déduplication par ID Strava) ; les nouvelles sont sauvegardées sur MongoDB
- **Carte de chaleur des courses** — génère une carte interactive dans le navigateur avec toutes les polylignes GPS superposées ; fond sombre CartoDB, chaque tracé en orange semi-transparent ; info-bulle avec nom et date au survol

### Thème
La barre supérieure inclut un bouton **☀ Clair / 🌙 Sombre** pour basculer entre le thème sombre (défaut, inspiré de GitHub/Strava) et le thème clair. La préférence n'est pas sauvegardée entre les sessions.

### Export
Depuis le menu **Exporter** :
- **PNG** — les cinq graphiques en haute résolution (180 dpi) *(nécessite une activité ouverte)*
- **PDF** — rapport 2 pages : résumé textuel + splits + graphiques *(nécessite une activité ouverte)*
- **CSV Splits** — splits kilomètre par kilomètre *(nécessite une activité ouverte)*
- **GPX** — exporte le tracé GPS au format GPX standard, compatible avec Garmin, Komoot, etc. *(nécessite une activité ouverte avec données GPS)*
- **CSV Statistiques** — exporte les statistiques mensuelles (km, courses, temps, allure, dénivelé) en CSV pour une analyse externe (Excel, etc.)

---

## Architecture technique

```
strava_viewer/
├── main.py                  # Point d'entrée — démarre StravaApp
├── config.py                # Constantes : couleurs, URL Strava, paramètres MongoDB
├── interval_detector.py     # Algorithme de détection d'intervalles (Python pur, aucune dépendance UI)
├── models.py                # Classe ActivityData — parsing JSON Strava, propriétés calculées
├── storage.py               # MongoStorage — sauvegarde/lecture des activités sur MongoDB
├── storage_manager.py       # Façade : gère la connexion MongoDB et le démarrage Docker
├── downloader.py            # OAuth2 Strava, téléchargement liste et détail des activités
├── docker-compose.yml       # MongoDB 7 sur le port 27017 (démarrage automatique)
└── ui/
    ├── __init__.py
    ├── app.py               # StravaApp (tk.Tk) — fenêtre principale, barre latérale, menu
    ├── widgets.py           # Widgets réutilisables : StatCard, make_scrollable, embed_mpl…
    ├── downloader_ui.py     # Fenêtre modale de téléchargement depuis Strava
    ├── export_pdf.py        # Génération PDF 2 pages avec matplotlib PdfPages
    ├── tab_calendar.py      # Onglet Calendrier mensuel
    ├── tab_dashboard.py     # Onglet Tableau de bord
    ├── tab_charts.py        # Onglet Graphiques + _build_export_fig() pour PNG/PDF
    ├── tab_hr.py            # Onglet Zones FC
    ├── tab_map.py           # Onglet Carte (ouvre le navigateur externe)
    ├── tab_gear.py          # Onglet Suivi d'équipement
    ├── tab_splits.py        # Onglet Splits
    ├── tab_intervals.py     # Onglet Détection d'intervalles
    ├── tab_best.py          # Onglet Meilleures performances
    ├── tab_compare.py       # Onglet Comparaison
    ├── tab_library.py       # Onglet Bibliothèque avec pagination
    ├── tab_stats.py         # Onglet Statistiques globales
    └── tab_raw.py           # Onglet JSON brut
```

### Stockage
L'application utilise **MongoDB** comme unique backend de stockage, géré par `StorageManager`. La connexion est tentée au démarrage dans un thread en arrière-plan ; si MongoDB n'est pas disponible, la Bibliothèque et les Statistiques resteront vides jusqu'à la connexion.

### Connexion MongoDB
`StorageManager.connect_mongo(auto_start=True)` tente :
1. Connexion directe à `localhost:27017`
2. En cas d'échec, exécute `docker compose up -d` et réessaie 5 fois (intervalle de 3s)

L'état de la connexion est visible dans la barre supérieure (● vert = connecté, ○ gris = hors ligne). Cliquer sur l'indicateur permet d'activer/désactiver manuellement.

### OAuth2 Strava
Le flux OAuth2 dans `downloader.py` :
1. Ouvre le navigateur sur le formulaire d'autorisation Strava
2. Démarre un serveur HTTP local sur `localhost:8765` dans un thread daemon
3. Capture le code d'autorisation depuis la redirection
4. Échange le code contre un access token + refresh token
5. Sauvegarde le token dans `.strava_token.json` (renouvellement automatique à l'expiration)

---

## Prérequis

- **Python 3.10+**
- **Docker Desktop** (optionnel, uniquement pour MongoDB)

### Dépendances Python

```
pip install requests folium matplotlib numpy pymongo tkinterweb
```

| Bibliothèque | Utilisation |
|---|---|
| `requests` | Appels API Strava |
| `folium` | Génération de carte HTML |
| `matplotlib` | Graphiques, export PNG/PDF |
| `numpy` | Ajustement de loi de puissance et simulation Monte Carlo (courbe de performance + prévision de course) |
| `pymongo` | Connexion MongoDB |
| `tkinter` | Interface graphique (inclus dans Python standard) |

---

## Démarrage

```bash
python main.py
```

---

## Configuration

Tous les paramètres se trouvent dans `config.py` :

```python
# MongoDB
MONGO_URI        = "mongodb://localhost:27017"
MONGO_DB         = "strava"
MONGO_COLLECTION = "activities"

# Token OAuth Strava sauvegardé dans
STRAVA_TOKEN_FILE = ".strava_token.json"

# Nombre maximum d'activités dans la comparaison
MAX_COMPARE = 5
```

### Configurer l'application Strava (premier accès)

1. Allez sur [https://www.strava.com/settings/api](https://www.strava.com/settings/api)
2. Créez une nouvelle application
3. Définissez **Authorization Callback Domain** sur `localhost`
4. Copiez **Client ID** et **Client Secret**
5. Dans l'app cliquez sur **Télécharger depuis Strava**, entrez les identifiants et cliquez sur **▶ DÉMARRER LE TÉLÉCHARGEMENT**
6. Le navigateur s'ouvrira pour l'autorisation — connectez-vous et autorisez
7. Le téléchargement démarrera automatiquement
8. Il peut être nécessaire de relancer la procédure dans les jours suivants en raison des limites de débit imposées par Strava

> **Note :** Pour télécharger les polylignes GPS (nécessaires pour la carte), l'application nécessite le scope `activity:read_all`. Strava le demande automatiquement lors de l'autorisation.

### MongoDB avec Docker

Si Docker Desktop est installé, MongoDB démarre automatiquement au premier lancement de l'application. Vous pouvez également le démarrer manuellement :

```bash
docker compose up -d
```

Pour l'arrêter :

```bash
docker compose down
```

Les données MongoDB sont sauvegardées dans un volume Docker persistant et survivent aux redémarrages.

---

## Notes opérationnelles

- La première fois que les courses sont téléchargées, le navigateur s'ouvre pour l'authentification Strava ; lors des sessions suivantes, le token est renouvelé automatiquement sans ouvrir le navigateur
- Le téléchargement est incrémentiel : les courses déjà présentes dans la base de données sont ignorées automatiquement
- La carte GPS nécessite une connexion internet pour charger les tuiles dans le navigateur (CartoDB, OpenStreetMap, Esri Satellite)
- L'export PDF nécessite `matplotlib` installé
- La carte de chaleur nécessite une connexion internet pour charger les tuiles CartoDB dans le navigateur

### Fichiers non suivis par git

| Fichier | Contenu |
|---|---|
| `.strava_token.json` | Token OAuth Strava (access + refresh token) |

## Utilisation de l'IA

- L'application a été entièrement réalisée en utilisant l'IA Claude Code avec le modèle Sonnet 4.6
