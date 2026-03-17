# ⬡ Strava Viewer 3.0

Aplicación de escritorio para analizar, visualizar y comparar actividades de carrera descargadas desde Strava. Interfaz gráfica nativa (tkinter), tema claro/oscuro y MongoDB como único backend de almacenamiento.

---

> Si este proyecto te es útil y quieres invitar al desarrollador a un café virtual, puedes hacerlo aquí → [☕ PayPal](https://paypal.me/TeoVr81). Sin presión — cada km cuenta, donación o no.

---

## Funcionalidades

### Apertura de actividades
- Descarga directamente todas tus carreras desde Strava con el botón **Descargar desde Strava** — las actividades se guardan en MongoDB

### Panel de control
Resumen completo de la actividad abierta:
- Distancia, tiempo activo/total, ritmo medio y mejor, velocidad
- Desnivel positivo y negativo
- Frecuencia cardíaca media y máxima, cadencia, calorías
- Índices de rendimiento (Suffer Score, VAM, etc.)

### Gráficos
Cinco gráficos integrados en la interfaz:
- **Ritmo por km** — barras de colores (verde = más rápido que la media, azul = en la media, rojo = más lento)
- **Velocidad** — línea con área rellena
- **Elevación** — gráfico de barras
- **Frecuencia cardíaca** — línea temporal
- **Cadencia** — tendencia por kilómetro

### Zonas FC
- Configuración manual de la frecuencia cardíaca máxima
- Distribución del tiempo por zona (Z1–Z5) con barras horizontales de colores
- Diagrama de dispersión FC vs ritmo con línea de tendencia y bandas de zona

### Mapa GPS
El mapa se abre en el **navegador predeterminado** (Chrome, Edge, Firefox…) e incluye:

- **Selector de capa** — cuatro fondos seleccionables desde el panel en la esquina superior derecha:
  - *Oscuro* (CartoDB dark matter, predeterminado)
  - *OpenStreetMap*
  - *Satélite* (Esri WorldImagery, imágenes satelitales reales, sin clave API)
  - *Claro* (CartoDB positron)
- **Trazado coloreado por ritmo** — la polilínea está dividida km a km con un degradado verde → amarillo → rojo (verde = km más rápido, rojo = km más lento); al pasar el cursor sobre cada segmento aparece el tooltip con ritmo, FC y desnivel del km
- **Marcadores kilométricos** — un indicador numerado por cada km completado; haciendo clic se abre un popup con ritmo, FC media y desnivel de ese kilómetro
- **Popups Inicio/Fin enriquecidos** — marcador verde (inicio) y rojo (fin) con popups completos: fecha, distancia, tiempo, ritmo medio/mejor, FC, desnivel, calorías, Suffer Score
- **Superposición de estadísticas** — barra fija en la parte superior del mapa con las métricas clave de la actividad (nombre, distancia, tiempo, ritmo, FC, desnivel)
- **Botón Pantalla completa** — expande el mapa a pantalla completa en el navegador
- **MiniMapa** — mapa panorámico 150×150 en la esquina inferior derecha para orientarse durante el zoom; activable/desactivable

Requiere el permiso de Strava `activity:read_all` para la polilínea GPS y una conexión a internet para cargar los mosaicos en el navegador.

### Splits
Tabla desplazable con los datos kilómetro a kilómetro:
- Distancia, tiempo, ritmo, velocidad, FC, desnivel, cadencia
- Color del ritmo para identificar inmediatamente los km más rápidos/lentos

### Mejores marcas
Lista de los mejores esfuerzos detectados por Strava (1 km, 5 km, 10 km, media maratón, maratón, etc.) con insignia 🏆 para los récords personales.

### Comparación
Comparación lado a lado de hasta 5 actividades:
- Tabla comparativa con resaltado verde (mejor) y rojo (peor) para cada métrica
- Gráfico de ritmo km a km superpuesto
- Gráfico de frecuencia cardíaca superpuesto
- Agregar actividades desde la pestaña Biblioteca con el botón ➕

### Biblioteca
Lista de todas las carreras guardadas en la base de datos, con:
- **Paginación** — 100 filas por página con navegación ◀ ▶
- **Filtros** por nombre/descripción, distancia (min–max km), rango de fechas y **Solo carreras** (filtra actividades con `workout_type = race`)
- Color del ritmo **semántico**: verde < 5:00/km, amarillo < 6:30/km, rojo por encima
- Hover sobre la fila con resaltado visual
- Abrir actividad con 📂, agregar a la comparación con ➕, eliminar con 🗑
- Indicador del estado de la conexión MongoDB

### Calendario
Vista mensual de todas las carreras con navegación mes a mes:
- Cada celda con una carrera muestra distancia, ritmo y frecuencia cardíaca; la intensidad del color naranja es **proporcional a los km recorridos** respecto al día más largo del mes (mapa de calor)
- Los días con varias carreras muestran un contador adicional con botones ◀ ▶ para desplazarse entre las carreras del mismo día
- Botones ◀ ▶ para navegar entre los meses, "Hoy" para volver al mes actual
- Hacer clic en una celda abre la actividad en la pestaña Panel de control
- El total de km y número de carreras del mes se muestra en el encabezado

### Estadísticas
Estadísticas agregadas sobre **todas** las carreras en la base de datos (ignora filtros y paginación):
- **Objetivo anual** — establece un objetivo de km para el año en curso con barra de progreso; el valor se guarda en `settings.json` y se recuerda entre sesiones
- Totales: carreras, km, horas, desnivel, ritmo medio, FC media, calorías, km/semana
- **Mapa de calor de actividades** — cuadrícula de calendario estilo GitHub de las últimas 52 semanas (filas = días de la semana Lun→Dom, columnas = semanas): cada celda está coloreada en naranja con intensidad proporcional a los km corridos ese día, gris oscuro si es día de descanso; barra de escala de color en la parte inferior; tooltip al pasar el cursor con fecha y km
- **Perfil atlético** — gráfico radar hexagonal con 6 dimensiones normalizadas 0–100: *Velocidad* (ritmo medio, escala 8:20→3:20/km), *Fondo* (mediana de distancias, escala 3→42 km), *Desnivel* (media m↑/km, escala 0→40 m/km), *Constancia* (% semanas con al menos una carrera en las últimas 52), *Volumen* (media km/semana en las últimas 52, escala 0→70), *Progresión* (comparación de ritmo medio últimos 3 meses vs 3 meses anteriores); junto a un panel con puntuaciones numéricas, barras proporcionales y descripción de cada dimensión
- **Tabla por mes** — últimos 12 meses con km, carreras, tiempo, ritmo medio, desnivel; gráfico de barras km por mes
- Tabla por año con km, carreras, tiempo, ritmo medio, desnivel; gráfico km por año y carreras por año
- Distribución de distancias (diagrama de tarta)
- **Carga de entrenamiento** — gráfico ATL/CTL/TSB (Banister TRIMP) de los últimos 12 meses:
  - *CTL (Forma física)* — media ponderada exponencial a 42 días
  - *ATL (Fatiga)* — media ponderada exponencial a 7 días
  - *TSB (Forma)* — CTL − ATL (positivo = descansado, negativo = fatigado)
- **Récords personales** — tabla con el mejor tiempo personal para las distancias canónicas (1 km, 5 km, 10 km, Media Maratón, Maratón), con nombre de actividad y fecha en que se consiguió
- **Análisis de pendiente (Grade Analysis)** — gráfico de barras del ritmo mediano dividido en 6 bandas de gradiente (desde descenso pronunciado <−8% hasta subida >8%), calculado a partir de los splits de 1 km registrados por Strava; filtros "Últimos días" y "Solo carreras"; los datos de este gráfico alimentan la corrección de desnivel personalizada de la Predicción de Rendimiento; botón ℹ con guía por banda y sugerencias de entrenamiento
- **Curva de rendimiento** — gráfico log-log distancia vs tiempo sobre los mejores esfuerzos (de 400m a la maratón) con ajuste de la ley de potencia `t = A × d^b`; los tiempos usados son el `moving_time` (pausas excluidas); filtros "Últimos días" y "Solo carreras"; el exponente `b` revela el perfil atlético (velocista vs fondista, comparación con b=1,06 de Riegel); botón ℹ con teoría y guía interpretativa
- **Predicción de rendimiento (Monte Carlo)** — estimación del tiempo sobre cualquier distancia con simulación de 5000 escenarios; parámetros configurables: distancia objetivo (estándar o personalizada en km), desnivel positivo del recorrido, ventana temporal del historial (últimos N días), longitud mínima y máxima de las carreras de las que obtener los mejores esfuerzos (km min/max), filtro solo carreras; la corrección de desnivel es personalizada: se calcula mediante regresión lineal sobre tus splits reales (seg/km por 1% de pendiente), con fallback al modelo Minetti si los datos son insuficientes; el resultado es un histograma con los percentiles P10/P25/P50/P75/P90 y un panel de diagnóstico con los datos usados en el ajuste, el coeficiente b y el tiempo base bruto; botón ℹ con guía completa sobre parámetros, cálculo e interpretación de resultados
- **Análisis de carreras y VDOT** — analiza todas las actividades clasificadas como "Carrera" en Strava (`workout_type = 1`) y calcula para cada una el VDOT según la fórmula de Jack Daniels (índice de capacidad aeróbica derivado de distancia y tiempo reales, sin test de laboratorio); muestra tres tarjetas de estadísticas (carreras totales, mejor VDOT, VDOT más reciente), un gráfico lineal de la evolución del VDOT en el tiempo con línea discontinua en el máximo histórico, una tabla de carreras paginada (10 por página, clicable para abrir la actividad) con fecha, km, tiempo, VDOT y nombre, y una tabla de predicciones para 1K / 5K / 10K / media maratón / maratón calculadas a partir del VDOT de la última carrera registrada; botón ℹ con explicación de la fórmula, tabla de valores de referencia (principiante → élite) y guía de interpretación de las predicciones
- **Rutas recurrentes** — detecta automáticamente las rutas que has corrido al menos 3 veces agrupando las actividades por zona de inicio (~300 m) y distancia (±1 km); para cada grupo muestra: lista desplazable con nombre más frecuente, distancia, número de carreras, período y ciudad/coordenadas; gráfico de dispersión del ritmo en el tiempo con coloración verde→rojo (más rápido→más lento), línea de tendencia discontinua, resaltado de la mejor carrera y la última; encabezado con mejor ritmo, ritmo medio e indicador de tendencia (mejorado/empeorado/estable); lista de las carreras del grupo con fecha, km, ritmo, FC y nombre, clicable para abrir la actividad; la ciudad se recupera primero de los metadatos de Strava, luego mediante geocodificación inversa Nominatim (OpenStreetMap) con caché persistente en MongoDB, hilo secuencial con pausa de 1 segundo entre las solicitudes para respetar el límite de velocidad

### Base de datos
Desde el menú **Base de datos** en la barra superior:
- **Exportar ZIP** — exporta todas las actividades de la base de datos en un archivo `.zip` (un archivo JSON por carrera); útil como copia de seguridad o para mover la base de datos a otra máquina
- **Importar ZIP** — importa un archivo `.zip` previamente exportado; las actividades ya presentes se omiten (deduplicación por ID de Strava); las nuevas se guardan en MongoDB
- **Mapa de calor de carreras** — genera un mapa interactivo en el navegador con todas las polilíneas GPS superpuestas; fondo oscuro CartoDB, cada trazado en naranja semitransparente; tooltip con nombre y fecha al pasar el cursor

### Tema
La barra superior incluye un botón **☀ Claro / 🌙 Oscuro** para cambiar entre el tema oscuro (predeterminado, inspirado en GitHub/Strava) y el tema claro. La preferencia no se guarda entre sesiones.

### Exportación
Desde el menú **Exportar**:
- **PNG** — los cinco gráficos en alta resolución (180 dpi) *(requiere actividad abierta)*
- **PDF** — informe de 2 páginas: resumen textual + splits + gráficos *(requiere actividad abierta)*
- **CSV Splits** — splits kilómetro a kilómetro *(requiere actividad abierta)*
- **GPX** — exporta el trazado GPS en formato GPX estándar, compatible con Garmin, Komoot, etc. *(requiere actividad abierta con datos GPS)*
- **CSV Estadísticas** — exporta las estadísticas mensuales (km, carreras, tiempo, ritmo, desnivel) en CSV para análisis externos (Excel, etc.)

---

## Arquitectura técnica

```
strava_viewer/
├── main.py                  # Punto de entrada — inicia StravaApp
├── config.py                # Constantes: colores, URLs de Strava, parámetros MongoDB
├── models.py                # Clase ActivityData — parsing JSON Strava, propiedades calculadas
├── storage.py               # MongoStorage — guardado/lectura de actividades en MongoDB
├── storage_manager.py       # Fachada: gestiona conexión MongoDB e inicio de Docker
├── downloader.py            # OAuth2 Strava, descarga lista y detalles de actividades
├── docker-compose.yml       # MongoDB 7 en el puerto 27017 (inicio automático)
└── ui/
    ├── __init__.py
    ├── app.py               # StravaApp (tk.Tk) — ventana principal, barra lateral, menú
    ├── widgets.py           # Widgets reutilizables: StatCard, make_scrollable, embed_mpl…
    ├── downloader_ui.py     # Ventana modal de descarga desde Strava
    ├── export_pdf.py        # Generación de PDF de 2 páginas con matplotlib PdfPages
    ├── tab_calendar.py      # Pestaña Calendario mensual
    ├── tab_dashboard.py     # Pestaña Panel de control
    ├── tab_charts.py        # Pestaña Gráficos + _build_export_fig() para PNG/PDF
    ├── tab_hr.py            # Pestaña Zonas FC
    ├── tab_map.py           # Pestaña Mapa (abre navegador externo)
    ├── tab_splits.py        # Pestaña Splits
    ├── tab_best.py          # Pestaña Mejores marcas
    ├── tab_compare.py       # Pestaña Comparación
    ├── tab_library.py       # Pestaña Biblioteca con paginación
    ├── tab_stats.py         # Pestaña Estadísticas globales
    └── tab_raw.py           # Pestaña JSON en bruto
```

### Almacenamiento
La aplicación utiliza **MongoDB** como único backend de almacenamiento, gestionado por `StorageManager`. La conexión se intenta al inicio en un hilo en segundo plano; si MongoDB no está disponible, la Biblioteca y las Estadísticas permanecerán vacías hasta la conexión.

### Conexión MongoDB
`StorageManager.connect_mongo(auto_start=True)` intenta:
1. Conexión directa a `localhost:27017`
2. Si falla, ejecuta `docker compose up -d` y reintenta 5 veces (intervalo de 3s)

El estado de la conexión es visible en la barra superior (● verde = conectado, ○ gris = sin conexión). Haciendo clic en el indicador se puede activar/desactivar manualmente.

### OAuth2 Strava
El flujo OAuth2 en `downloader.py`:
1. Abre el navegador en el formulario de autorización de Strava
2. Inicia un servidor HTTP local en `localhost:8765` en un hilo daemon
3. Captura el código de autorización desde la redirección
4. Intercambia el código por access token + refresh token
5. Guarda el token en `.strava_token.json` (renovación automática al vencimiento)

---

## Requisitos

- **Python 3.10+**
- **Docker Desktop** (opcional, solo para MongoDB)

### Dependencias Python

```
pip install requests folium matplotlib numpy pymongo tkinterweb
```

| Biblioteca | Uso |
|---|---|
| `requests` | Llamadas a la API de Strava |
| `folium` | Generación de mapa HTML |
| `matplotlib` | Gráficos, exportación PNG/PDF |
| `numpy` | Ajuste de ley de potencia y simulación Monte Carlo (curva de rendimiento + predicción de carrera) |
| `pymongo` | Conexión MongoDB |
| `tkinter` | Interfaz gráfica (incluido en Python estándar) |

---

## Inicio

```bash
python main.py
```

---

## Configuración

Todos los parámetros se encuentran en `config.py`:

```python
# MongoDB
MONGO_URI        = "mongodb://localhost:27017"
MONGO_DB         = "strava"
MONGO_COLLECTION = "activities"

# Token OAuth de Strava guardado en
STRAVA_TOKEN_FILE = ".strava_token.json"

# Número máximo de actividades en la comparación
MAX_COMPARE = 5
```

### Configurar la aplicación Strava (primer acceso)

1. Ve a [https://www.strava.com/settings/api](https://www.strava.com/settings/api)
2. Crea una nueva aplicación
3. Establece **Authorization Callback Domain** en `localhost`
4. Copia **Client ID** y **Client Secret**
5. En la app haz clic en **Descargar desde Strava**, introduce las credenciales y haz clic en **▶ INICIAR DESCARGA**
6. El navegador se abrirá para la autorización — inicia sesión y autoriza
7. La descarga comenzará automáticamente
8. Puede ser necesario reiniciar el procedimiento en los días siguientes debido a los límites de velocidad impuestos por Strava

> **Nota:** Para descargar las polilíneas GPS (necesarias para el mapa), la app requiere el scope `activity:read_all`. Strava lo solicita automáticamente durante la autorización.

### MongoDB con Docker

Si Docker Desktop está instalado, MongoDB se inicia automáticamente en el primer lanzamiento de la app. Alternativamente puedes iniciarlo manualmente:

```bash
docker compose up -d
```

Para detenerlo:

```bash
docker compose down
```

Los datos de MongoDB se guardan en un volumen Docker persistente y sobreviven a los reinicios.

---

## Notas operativas

- La primera vez que se descargan las carreras se abre el navegador para la autenticación de Strava; en sesiones posteriores el token se renueva automáticamente sin abrir el navegador
- La descarga es incremental: las carreras ya presentes en la base de datos se omiten automáticamente
- El mapa GPS requiere una conexión a internet para cargar los mosaicos en el navegador (CartoDB, OpenStreetMap, Esri Satellite)
- La exportación PDF requiere `matplotlib` instalado
- El mapa de calor requiere una conexión a internet para cargar los mosaicos CartoDB en el navegador

### Archivos no rastreados por git

| Archivo | Contenido |
|---|---|
| `.strava_token.json` | Token OAuth de Strava (access + refresh token) |
| `settings.json` | Preferencias de usuario locales (ej. objetivo de km anual) |

## Uso de IA

- La aplicación fue completamente desarrollada usando la IA Claude Code con el modelo Sonnet 4.6
