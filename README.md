# Los Ángeles · sistema de información

Grupo: Jeronimo Escobar Restrepo · Juan José Álvarez Ocampo · Enlace: https://los-angeles-lemon.vercel.app · Revisado: 2026-11-03

Repositorio: https://github.com/jalvarez01/Los-Angeles. El sitio es abierto y sin compuerta: solo publica agregados de fuentes públicas (ver «Protección»).

## Para quién y qué pregunta

- **Usuario:** un concejal del Ayuntamiento de Los Ángeles y su equipo, que necesitan comparar su distrito con los otros 14 y con la ciudad.
- **Preguntas:** las tres de la entrega 1 (ver «Preguntas: respondidas y pendientes»).
- **Escala y comparación:** la ciudad (FIPS 06-44000) y sus 15 distritos de consejo; la seguridad, en las 21 áreas y los 1.135 distritos de reporte de LAPD, porque esas geografías no se cruzan con las del Ayuntamiento.
- **Lo que decidimos no mostrar, y por qué:** ningún registro individual de delitos, solicitudes 311 ni permisos (ubicaciones por cuadra, hora, número de predio, marcas de violencia doméstica), y ningún conteo de 1 a 9 ofensas por distrito de reporte. Con esos datos se puede llegar a la casa de una persona (respuesta 5 de la entrega 1).

## Preguntas: respondidas y pendientes

La sección «00 Preguntas» del sitio repite esto con las cifras del día, que se calculan desde el lago al cargar la página.

| Pregunta | Estado | Dónde se responde | Qué muestra hoy |
|---|---|---|---|
| ¿Dónde se concentran los delitos y cómo cambian mes a mes? | Respondida | Sección 02 Seguridad: mapa por área, mapa por distrito de reporte y serie mensual | Ofensas de 12 meses por área de LAPD, en total y por 10.000 habitantes ± MOE (F01, F18, F07; vigencia 2025-10 a 2026-09) |
| ¿Qué piden los vecinos, en qué distritos y cuánto se resuelve? | Respondida | Sección 03 311 y mapa 08 | Solicitudes del año, % cerradas con y sin Information-Only, por tipo y por distrito, con tasa ± MOE (F03, F07; vigencia 2026-01 a 2026-10) |
| ¿Dónde se construye y cuánta vivienda se suma? | Respondida | Sección 04 Vivienda y mapa 08 | Permisos y unidades netas de 12 meses por distrito, con tasa ± MOE (F04, F07; vigencia 2025-11 a 2026-10) |
| ¿Cuántas ofensas hay en cada distrito de consejo? | Pendiente | | LAPD no reporta por distrito de consejo y cruzar las geografías exige ubicaciones individuales, que decidimos no bajar. Haría falta que LAPD publicara los conteos por distrito de consejo. |
| ¿Cuánto gasta la ciudad y en qué? | Pendiente | | No hemos buscado el presupuesto municipal (respuesta 6 de la entrega 1). Queda para el siguiente rastreo. |
| ¿Cómo está la calidad del aire? | Pendiente | | Descartamos AirNow (F13) por sus términos (respuesta 3). Las imágenes de Sentinel-2 que anotamos como alternativa todavía no están integradas. |

## Entregas

- `entrega1/Diccionario_de_datos_LosAngeles.xlsx`: 18 fuentes (F01 a F16, F18 y F19; la foto F17 solo está en `catalogo/`), 143 campos (uno por cada campo real de `lago/` y `territorio/`), la bitácora de IA (24 encargos) y el resumen con sus valores calculados.
- `entrega1/LosAngeles.docx`: las seis respuestas de la entrega 1. Sus cifras corresponden al lago construido el 2026-10-06; el lago se ha reconstruido desde entonces, así que las cifras actuales no coinciden con las del Word.
- `catalogo/`: una ficha por fuente (`F01.json` a `F19.json`), generadas desde `catalogo/fuentes.py`.
- Entrega 2: el sitio publicado, este README, la carpeta `exploracion/` y el Excel actualizado.

## La réplica

- Replicamos del Cerebro Lima el contrato del lago (`tema`, `probado`, `fuentes`, `cifras`, `series`), un script de ingesta por fuente, la verificación que falla y el catálogo con las fuentes caídas y descartadas.
- Cambiamos: agregamos `tablas` al contrato para los desgloses por zona; la seguridad se agrega en el servidor de la fuente y no se baja nunca un registro; usamos Leaflet y Chart.js en vez de MapLibre (ver «Bitácora de exploración»); y no hay compuerta.
- Fuentes catalogadas: 19 (11 integradas al lago, F17 integrada solo a la capa web, 6 descartadas, 1 que no existe). Ver `catalogo/`.
- Huecos: no hay población oficial por distrito de consejo (la aproximamos con el ACS), no hay delitos por distrito de consejo y no buscamos aún el presupuesto.

## El lago

| Archivo | Fuente | Qué trae |
|---|---|---|
| `lago/seguridad.json` | F01, F07, F18, F19 | ofensas NIBRS de los últimos 12 meses completos de la fuente, por categoría (suman el total), por mes, por área de LAPD (población del ACS, tasa por 10.000 habitantes, su MOE y la marca de diferencia con la ciudad, que solo considera el error del ACS) y por distrito de reporte (celdas con menos de 10 suprimidas) |
| `lago/municipio.json` | F03, F07 | solicitudes 311 del año, % cerradas (con y sin Information-Only), por tipo, por distrito (tasa ± MOE y prueba contra la ciudad) y por mes |
| `lago/vivienda.json` | F04, F07 | permisos y unidades netas de 12 meses, por distrito (tasas ± MOE y prueba contra la ciudad) y por mes |
| `lago/demografia.json` | F06, F07 | población y viviendas de la ciudad (F06); natalidad de la ciudad, California y EE. UU. con MOE, serie anual de la ciudad con MOE, y población y natalidad por distrito de consejo con MOE (F07) |
| `lago/movilidad.json` | F09 | bicicleta compartida en tiempo real y las estaciones con nombre, coordenadas, bicis y anclajes |
| `lago/equipamientos.json` | F10, F12, F07 | hoteles, hospitales, colegios y parques en OpenStreetMap; colegios, hospitales y parques por distrito (conteo, tasa ± MOE y prueba contra la ciudad; sin coordenadas) |
| `lago/escucha.json` | F11 | vistas del artículo «Los Ángeles» en Wikipedia |
| `territorio/distritos_consejo.geojson` | F12 | 15 distritos de consejo, simplificados (~300 m) |
| `territorio/areas_lapd.geojson` | F18 | 21 áreas de LAPD, simplificadas (~300 m) |
| `territorio/distritos_reporte_lapd.geojson` | F19 | 1.135 distritos de reporte de LAPD, simplificados (~50 m) |

Contrato: el de Lima más nuestra extensión `tablas` (`unidad`, `vigencia`, `fuente`, `columnas`, `filas`; opcionales `nota`, `nota_moe` y `referencia_ciudad`).

**Margen de error.** Toda tasa lleva al lado su columna `_moe` (90 % de confianza, como lo publica el Census Bureau). La población de cada zona suma los sectores censales cuyo punto interno cae en ella, y su MOE es la raíz de la suma de los MOE² de esos sectores, la aproximación del Census Bureau para estimaciones derivadas. Una tasa con conteo exacto hereda MOE = tasa × MOE_pob / pob. La natalidad usa la fórmula de proporción del Census Bureau. La columna `_dif_significativa` aplica la prueba del Census Bureau contra la ciudad (|r − r_ciudad| / raíz(EE² + EE_ciudad²) > 1,645). El alcance de la prueba no es el mismo en todas las tablas. En natalidad, donde el numerador y el denominador son estimaciones del ACS, cubre todo el error de muestreo: 9 de los 15 distritos no se distinguen de la ciudad (difieren D4, D5, D7, D9, D13 y D15) (39,5 ± 1,4 nacimientos por 1.000 mujeres). En 311, permisos, delitos y equipamientos el MOE solo cubre el denominador (la población del ACS) y toma el conteo como exacto, sin modelar su variación aleatoria de un año a otro; ahí la marca casi siempre sale verdadera (14 de 15 distritos en 311, 20 de 21 áreas en delitos), pero es una cota inferior de la incertidumbre, no la prueba de que la diferencia sea real.

**Supresión.** En seguridad por distrito de reporte, toda celda con 1 a 9 ofensas se guarda como `null` con `suprimido = true`, nunca el número; si en un área queda una sola celda suprimida, se suprime también la visible más pequeña, para que no se despeje restando del total del área. Hoy son 28 celdas: 25 con 1 a 9 ofensas y 3 complementarias.

LAPD carga los delitos con unas semanas de rezago, así que la ventana de seguridad termina en el último mes completo que tiene la fuente.

## Cómo se reconstruye

```
rm -rf lago territorio
for s in ingesta/pull_*.py; do python3 "$s"; done
python3 verificacion/verificar.py
git diff --stat -- lago/ territorio/
```

Solo biblioteca estándar de Python (3.10 o más). Una sola llave: `CENSUS_API_KEY` (gratuita, en https://api.census.gov/data/key_signup.html) en un archivo `.env` en la raíz, que está en `.gitignore` y nunca se sube; sin ella se detienen `pull_natalidad.py`, `pull_seguridad.py` y `pull_equipamientos.py`. Overpass (F10) a veces responde 502 o 504: `pull_equipamientos.py` reintenta solo. data.lacity.org a veces responde 500 o se corta: se vuelve a correr ese script. `verificar.py` falla si falta un tema o una capa. La última reconstrucción completa fue el 2026-11-03 (178 s) y terminó con 0 fallos en 214 comprobaciones.

## Capa web

Publicada en https://los-angeles-lemon.vercel.app. `web/` es un sitio estático que lee solo `lago/` y `territorio/`, sin llamadas en vivo; la llave del Censo nunca llega al navegador. Se prueba con `python3 web/build.py && python3 -m http.server -d web/dist`.

- **Procedencia a un clic.** Cada cifra, gráfico y mapa tiene un botón «i» (accesible con teclado y al tacto) que abre la fuente con su ID enlazado a su ficha en «Gobernanza», la licencia como la publica la fuente, la vigencia, la fecha de prueba del archivo del lago y si es PROXY. Junto a cada número va también, en pequeño, su ID y su vigencia.
- **PROXY.** Marcamos con una etiqueta PROXY toda cifra aproximada: la población y la natalidad por zona (asignación por sectores censales), toda tasa per cápita que usa esa población, las estimaciones del ACS y del DOF, y los conteos de OpenStreetMap (cobertura voluntaria). Los conteos administrativos (ofensas, 311, permisos, estaciones) no son PROXY.
- **Margen de error.** Los tooltips de los mapas dan valor ± MOE y la marca de diferencia con la ciudad; en las tasas con conteo exacto dicen que esa marca solo considera el error del ACS. Los gráficos de tasas por zona tienen barras de error y una línea que explica que dos barras que se traslapan no son una diferencia significativa, y que en esas tasas unas barras separadas no prueban que la diferencia sea real.
- **Dos geografías.** La seguridad se muestra solo en áreas y distritos de reporte de LAPD; los distritos de consejo tienen su propia vista, sin ofensas. Ningún mapa superpone las dos geografías. El mapa de estaciones de bicicleta dibuja los contornos de los distritos de consejo solo como referencia.
- **Mapas** (Leaflet, sin teselas externas): ofensas por área de LAPD (total o por 10.000 habitantes); ofensas por distrito de reporte con las celdas suprimidas rayadas y un selector para acercar a cada área; los 15 distritos de consejo con 311, permisos, población, natalidad y equipamientos; estaciones de Metro Bike Share.
- Abre en un teléfono: lo probamos a 390 px sin desplazamiento horizontal. El sitio pesa 1,1 MB.

Diseño: inspirado en los menús de pausa de los videojuegos de mundo abierto, sin recursos de terceros del juego; tipografías Anton e IBM Plex Sans (Google Fonts). Fotografía de fondo: «Echo park lake with lotus flowers and Los Angeles skyline in the background», de Alaiben, CC BY-SA 4.0, vía [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Echo_park_lake_with_lotus_flowers_and_Los_Angeles_skyline_in_the_background.jpg) (F17, en `web/assets/fondo-los-angeles.jpg`, 2400 × 1515 px y 452.634 bytes; la gradación de color es solo CSS).

## Decisiones

**Qué mostramos.** Conteos y tasas por zona, con su margen de error y su procedencia a un clic, para que un concejal compare su distrito con los demás y con la ciudad. No mostramos registros individuales, ni conteos pequeños por distrito de reporte, ni ofensas por distrito de consejo. Lo que es aproximado lleva la etiqueta PROXY.

**¿Se puede usar?** Cada licencia está copiada como la publica la fuente (tabla «¿Se puede usar?» y columna H del Excel). Las que piden atribución la tienen en el pie del sitio: el Censo (F07), OpenStreetMap (F10), la foto (F17) y los límites de LAPD (F18). Las que no declaran licencia (F01, F04, F06, F09, F12, F19) son publicaciones de gobierno en portales abiertos; las usamos solo agregadas y lo decimos en cada ficha.

**Cómo lo protegimos.** Agregamos en el servidor de cada fuente: al lago solo llegan conteos. Suprimimos las celdas con menos de 10 ofensas y una complementaria por área cuando hace falta. No guardamos coordenadas de personas: las únicas coordenadas del lago son las de las estaciones de bicicleta, que son infraestructura pública, y los equipamientos se asignan a distritos al ingerir sin guardar su ubicación. El verificador falla si encuentra un conteo de 1 a 9, un campo con nombre de dato personal, un correo, un teléfono o un número de seguro social. No hay secretos en el repositorio ni en el navegador (ver «Protección»).

**Con qué herramienta y por qué.** Necesitábamos mostrar cifras con su procedencia a un clic, mapas de dos geografías y barras de error, en un teléfono. Teníamos que proteger a las personas detrás de los registros, y eso lo resuelve la agregación antes del lago, no la herramienta. HTML con Leaflet y Chart.js, publicado en Vercel, cumple las dos cosas: los datos quedan en nuestro repositorio, se rehace con un comando y no pide cuenta. Casi elegimos MapLibre GL JS, que dibuja mejor y tiene licencia BSD, pero necesita WebGL y cambió su forma de cargarse en la versión 6; para 15 polígonos y un coroplético de 1.135 no lo necesitábamos.

## Protección

- **Nivel:** abierto, solo agregados. No hay compuerta: todo lo que se publica son conteos y tasas de fuentes públicas, así que una clave sería teatro (la guía lo dice así) y daría la apariencia de proteger algo que no hace falta proteger. Lo que había que proteger (los registros individuales) nunca llega al repositorio ni al despliegue.
- **Qué protegemos, y de quién:** a las personas detrás de los registros de F01 y F03, de cualquiera que cruce una ubicación o una fecha con otra fuente. Y la llave del Censo, de quien lea el repositorio o el sitio.
- **Pruebas de terminal:** `curl` a `/`, a cada archivo de `lago/` y de `territorio/` (200, a propósito: es lo publicado), y a `/.env`, `/.env.local` y `/lago/raw/` (404). Las repetimos en producción después de cada despliegue.
- **Revisión de secretos en el historial:** `git log -p --all | grep -i -E "clave|secret|password|api_key|token"` da 83 coincidencias, todas nombres de variables (`CENSUS_API_KEY`), la palabra «clave» en textos y el paquete `css-tokenizer` de un `package-lock`. El valor de la llave no aparece en el historial, ni en `web/dist`, ni en ningún archivo del repositorio; `.env` nunca se subió.

## Bitácora de exploración

Probamos cada herramienta con los mismos datos del lago. Las de vistas hicieron el mismo coroplético de 311 por 10.000 habitantes. Las capturas son la salida real del 2026-11-03.

| Tramo | Herramienta | Qué pidió para empezar | Licencia | Dónde quedan los datos | ¿Se rehace con un comando? | Estado del proyecto (última versión) | Qué resolvió de nuestra pregunta | Qué no pudo | ¿Quedó? ¿Por qué? |
|---|---|---|---|---|---|---|---|---|---|
| Vistas | HTML + Leaflet 1.9.4 + Chart.js 4.4.1 (el sitio) | nada: dos scripts de cdnjs | BSD-2-Clause y MIT (OSI) | en nuestro repositorio y en Vercel | sí: `python3 web/build.py` | Leaflet 1.9.4 es la última estable; Chart.js va en 4.6.1 | todo: procedencia, barras de error, dos geografías, 390 px | barras de error: las dibujamos con un complemento propio de pocas líneas | sí: cumple todo sin cuenta ni WebGL, y lo controlamos entero |
| Vistas | MapLibre GL JS 6.16.0 (`exploracion/maplibre/`) | nada, pero necesita WebGL (en Chrome sin interfaz hubo que activar SwiftShader) | BSD-3-Clause (OSI) | en nuestro repositorio; la librería desde unpkg | sí: un `http.server` en la raíz | 6.16.0, del 25-oct-2026 | el coroplético con popup ± MOE, sin teselas | la versión 6 ya no publica `dist/maplibre-gl.js` (404): solo un módulo ES; los gráficos con barras de error habría que hacerlos aparte | no, por poco: mejor mapa, pero WebGL y otro motor solo para mapas |
| Vistas | Observable Framework 1.13.4 (`exploracion/observable/`) | npm: 260 paquetes y 81 MB; dos (esbuild) traen scripts de instalación, que no corrimos (`--ignore-scripts`) | ISC (OSI) | los cargadores copian el lago dentro del sitio: queda como un archivo más de lo publicado | sí: `npx observable build` | 1.13.4, del 2-mar-2026; sin versión nueva desde entonces | el coroplético y la natalidad con barras de error y la ciudad como referencia | el mapa salió como un cuadrado negro hasta invertir el sentido de los anillos del GeoJSON; necesita red al construir para bajar sus módulos | no: 260 dependencias para dos gráficos, y el proyecto está quieto |
| Vistas | Datawrapper, Power BI, Data Studio (Looker Studio), Tableau Public, Flourish | cuenta | propietarias | en el servicio | no | no lo revisamos | consideradas, no probadas | piden cuenta, y en el plan gratuito lo publicado es público y descargable (guía, lámina «La herramienta») | no: no las probamos por la cuenta |
| Vistas | Streamlit | pip (Python); Community Cloud pide cuenta | Apache-2.0 | en el repositorio y en la aplicación | sí | 1.66.1 | considerada, no probada | elegimos Observable para la segunda prueba porque deja un sitio estático, como el nuestro | no la probamos |
| Ingesta | Python solo con biblioteca estándar (`ingesta/`) | nada | PSF (OSI) | en `lago/` | sí: el bucle de `pull_*.py` | Python 3.15 | todas las fuentes, con agregación en el servidor | nada que nos faltara | sí: sin dependencias que mantener |
| Ingesta | DuckDB 2.0.0 (`exploracion/duckdb/`) | pip en un entorno aparte (1 paquete); al leer una URL descargó solo la extensión httpfs (19,7 MB) en `~/.duckdb` | MIT (OSI) | en memoria; no escribe nada | sí | 2.0.0, del 21-oct-2026 | leyó la API de Wikipedia (F11) desde la URL y dio el mismo último mes que el lago | el código escrito para la versión 1 falló: la 2.0 quitó `fetchone()` | no: no nos ahorra nada frente a urllib y trae código que se baja solo |
| Verificación | `verificacion/verificar.py` | nada | nuestro | lee `lago/` | sí | no aplica | 214 comprobaciones, incluidas las de MOE y supresión; las rompimos a propósito y fallan | nada que nos faltara | sí |
| Verificación | DuckDB 2.0.0 con SQL | lo mismo que arriba | MIT (OSI) | en memoria | sí | 2.0.0 | rehízo dos comprobaciones (las áreas suman el total; ningún conteo de 1 a 9) y dio lo mismo | las pruebas de MOE en SQL serían más largas que en Python | no: el verificador ya cubre lo mismo sin dependencias |
| Rastreo | API del catálogo de Socrata y buscador de ArcGIS Hub (GeoHub) | nada | no aplica (servicios de los portales) | no guardan nada | sí, con curl | en servicio | encontraron F18 y F19 y sus licencias | el buscador de GeoHub mezcla capas del condado y de otras cuentas: hay que filtrar por dueño | sí, las dos |
| Protección | curl y Chrome sin interfaz | nada (puppeteer-core en una carpeta aparte, fuera del repositorio) | curl (MIT) y Chrome | no guardan nada | sí | en servicio | los 200 y 404 de la terminal, y que todo se vea y abra sin bypass | nada que nos faltara | sí, las dos |

## Bitácora de IA

Resumen de la hoja «3. Bitácora IA» del Excel, con las 12 filas nuevas de esta entrega. Usamos Claude (Claude Code) con acceso al repositorio, a la terminal y a nuestras sesiones de GitHub y Vercel; todo lo que propuso lo corrimos y lo comprobamos antes de aceptarlo. De 24 encargos, 4 salieron bien a la primera, 9 fueron parciales y 11 fueron incorrectos o inventados.

| # | Tramo | Herramienta | Qué le encargamos | Qué entregó | Qué le corregimos | Resultado |
|---|---|---|---|---|---|---|
| 1 | Rastreo | Claude | Dónde encontrar información en tiempo real de Los Ángeles para un sistema como el Cerebro Lima | Propuso data.lacity.org y GeoHub, la API en tiempo real de Metro, Metro Bike Share, crimen de LAPD, 311, AirNow, Census y NOAA | Abrimos cada enlace. El portal y Bike Share respondieron; AirNow pide cuenta y sus términos prohíben usarlo para decisiones públicas; el Census pide llave | Parcial |
| 2 | Rastreo | Claude | Describir el conjunto de crimen de LAPD para el catálogo | El conjunto 2nrs-mtv8 con vigencia «actualizado semanalmente» | Consultamos max(date_rptd): 2025-03-28. El nombre oficial es «Crime Data from 2020 to 2024»; LAPD pasó a NIBRS el 2024-03-07 | Incorrecto |
| 3 | Rastreo | Claude | La URL del feed GBFS de Metro Bike Share | gbfs.bcycle.com/bcycle_metrobikeshare/… | Respondió 404. La URL real (bcycle_lametro) salió de la página de datos de bikeshare.metro.net | Inventado |
| 4 | Verificación | Claude | Cuántas estaciones tiene Bike Share | 178 estaciones | Contamos las estaciones del JSON completo: 224 | Incorrecto |
| 5 | Rastreo | Claude | Un conjunto de permisos de construcción de la ciudad | Primero el ID yv23-pmwf; después hbkd-qubn | yv23-pmwf respondió 403. hbkd-qubn es una vista de 2023 con nombres de personas. Buscando en el catálogo del portal apareció pi9x-tg5x, al día (2026-09-26) y sin nombres | Parcial |
| 6 | Rastreo | Claude | Los límites de los distritos de consejo | El conjunto 872g-cjhh «City Council Districts» del catálogo de Socrata | En data.lacity.org dio 404: era de otro portal que el catálogo federado mezcló. Los límites reales salieron de LA GeoHub | Incorrecto |
| 7 | Rastreo | Claude | APIs de transporte público de Los Ángeles | Entre sus resultados, una ficha de publicapi.dev con la ruta api.metro.net/bus/stops | La ruta respondió 404; la ficha describe endpoints que Metro no publica | Inventado |
| 8 | Rastreo | Claude | Una fuente de población de la ciudad sin llave | Census ACS (pide llave); como alternativa, el informe E-1 del Departamento de Finanzas de California | El Census redirigió a missing_key. En el Excel del DOF hay dos filas «Los Angeles»: condado 9.837.286 y ciudad 3.806.201; tomamos la ciudad y el script lo comprueba | Parcial |
| 9 | Rastreo | Claude | Una fuente de «escucha» como la de Lima | Google News RSS | El acceso automatizado fue rechazado por robots.txt. Se reemplazó por el script base del taller (Wikipedia), comprobando que «Los Ángeles» es artículo y no desambiguación | Parcial |
| 10 | Ingesta | Claude | Cómo consultar OpenStreetMap dentro del límite de la ciudad | La consulta a Overpass por el área de la relación 207359 | La primera prueba (27-sep) no llegó al servidor; desde el 28-sep responde, y comprobamos que el área es la ciudad (admin_level 8) y no el condado | Correcto |
| 11 | Permiso | Claude | La licencia de cada fuente | «Abierta explícita» para LAPD y para los permisos | Leímos los metadatos del portal: NIBRS y los permisos vigentes no declaran licencia; el crimen viejo y el 311 son CC0; la vista de permisos de 2023 es CC BY 4.0 | Incorrecto |
| 12 | Ingesta | Claude | El script de ingesta de seguridad | Un script que toma los últimos 12 meses completos del calendario | Al correrlo el 2026-10-05, septiembre traía 10.097 ofensas frente a unas 18.000 de un mes normal: LAPD solo tenía cargado hasta el 19 de septiembre. Cambiamos el script para que la ventana termine en el último mes completo de la fuente | Parcial |
| 13 | Permiso | Claude | Auditar el repositorio antes de la entrega 2 | La foto de fondo del repositorio no era la acreditada: el commit «foto los angeles» la había cambiado por otra imagen sin autor ni licencia (perfil ICC «Google Inc. 2016») | Comparamos las dos versiones de la imagen y la que servía producción; restauramos la de Echo Park (Alaiben, CC BY-SA 4.0) | Correcto |
| 14 | Verificación | Claude | Confirmar que la foto restaurada es la que sirve producción | Reportó el hash e6e156c8… como SHA-256 | Al calcular SHA-256 a propósito salió 905d536c…: el primero era SHA-1 | Incorrecto |
| 15 | Rastreo | Claude | Buscar los límites oficiales de las 21 áreas y de los distritos de reporte de LAPD | Los ítems «LAPD Divisions» y «LAPD Reporting District» de LA GeoHub, con su licencia | Bajamos los GeoJSON sin llave y cruzamos los códigos con F01: 21 de 21 áreas y 1.132 de 1.135 distritos | Correcto |
| 16 | Protección | Claude | Resumir la supresión de celdas con menos de 10 ofensas | «Complementarias: 0» en el resumen final, después de haber dicho 28 = 25 + 3 | Recalculamos desde F01: 25 celdas de 1 a 9 y 3 complementarias en las áreas 1, 12 y 21. El 0 salía de una expresión con «and False» | Incorrecto |
| 17 | Ingesta | Claude | Reintentar los scripts que fallaron por red durante la reconstrucción | Un bucle con el comando timeout | En macOS no existe timeout: cada reintento fallaba aunque la red ya hubiera vuelto | Incorrecto |
| 18 | Verificación | Claude | Revisar por qué el verificador dio 0 fallos con Overpass caído | El verificador no exigía los siete temas: faltaba equipamientos.json y pasaba igual | Borramos un tema a propósito y vimos el FAIL después del arreglo | Correcto |
| 19 | Contrato | Claude | Calcular el margen de error de las tasas por 10.000 habitantes | MOE redondeado con los mismos decimales que la tasa | En equipamientos el MOE quedaba en 0,0 y todas las zonas salían «significativas»; se guardó con un decimal más | Parcial |
| 20 | Vistas | Claude | Escribir la respuesta a la pregunta de delitos con cifras del lago | Una frase con «Central» escrito a mano | Revisamos la prosa: el nombre del área debía salir del lago, como las cifras | Parcial |
| 21 | Exploración | Claude | Prototipo del mapa con MapLibre GL JS | Cargar dist/maplibre-gl.js con un script clásico | unpkg respondió 404: la versión 6 solo publica el módulo ES (maplibre-gl.mjs) | Parcial |
| 22 | Exploración | Claude | Prototipo del mapa con Observable Framework | El coroplético con Plot.geo sobre la capa de distritos | Salió un cuadrado negro: d3-geo leía los anillos al revés; se invirtió su sentido | Parcial |
| 23 | Exploración | Claude | Consultas de prueba con DuckDB 2.0 | Código con fetchone() | DuckDB 2.0 quitó fetchone() de las relaciones; se cambió por fetchall() | Incorrecto |
| 24 | Despliegue | Claude | Desplegar la primera versión del sitio con la CLI de Vercel | Un despliegue que quedó en producción sin querer | vercel ls lo mostró como Production | Incorrecto |

## Nuestra posición

**«Público no es inocuo»** (reflexiones de gestión y gobierno de datos). Todas nuestras fuentes de seguridad y de 311 son públicas, y aun así no las publicamos como vienen. Un registro de F01 trae la cuadra, la fecha, la hora y la marca de violencia doméstica; ninguno de esos campos dice quién es la víctima, pero juntos y cruzados con un directorio la señalan. Por eso el lago solo guarda conteos que calcula el servidor de la fuente, y por eso el conteo mínimo que exigimos por distrito de reporte es 10: con menos, una celda describe a muy pocas personas en una zona de pocas cuadras. Aprendimos además que el umbral solo no basta. Como publicamos el total de cada área, una única celda oculta se despejaba restando, así que suprimimos una celda más en esas áreas (3 de las 28 de hoy). Lo defendemos aunque cueste precisión: el mapa de distritos de reporte tiene 28 zonas rayadas que un concejal no puede leer, y preferimos eso a que alguien pueda llegar a una casa.

**«Explorar es ampliar la superficie de ataque»** (reflexiones de ciberseguridad). El sistema publicado no instala nada: la ingesta es solo biblioteca estándar y la web carga dos librerías conocidas desde cdnjs. La exploración fue otra cosa. Observable Framework trajo 260 paquetes, de los que no sabríamos nombrar más de diez; dos de ellos (esbuild) traen scripts de instalación, que no dejamos correr. DuckDB, que se instaló como un solo paquete, bajó por su cuenta 19,7 MB de una extensión en una carpeta de nuestro usuario, fuera del entorno virtual que habíamos preparado para aislarlo. Por eso cada prototipo vive en `exploracion/`, con sus dependencias fuera de git y sin acceso a `.env`, y ninguna de esas herramientas entró al sistema. Si mañana uno de esos paquetes resultara comprometido, el sitio no cambia; lo que haríamos es borrar `node_modules`, `.venv` y `~/.duckdb` y revisar que nada haya tocado el repositorio.

## Revisión cruzada

- Tres cifras auditadas por otro grupo: pendiente; todavía no hemos recibido la revisión.
- Ataque de otro grupo: pendiente. Como no hay compuerta, el ataque no tiene clave que romper: lo que cabe probar es que no salgan registros individuales ni conteos suprimidos, y que `/.env` y `/lago/raw/` den 404.
- Vueltas atrás en la ruta: de las vistas al contrato, para agregar el MOE y la prueba de significancia que pidió el profesor; de la verificación a la ingesta, cuando el verificador pasaba con un tema faltante; de la curaduría a la capa web, cuando la foto de fondo no tenía licencia.

## ¿Se puede usar?

| Fuente | Licencia (como la publica la fuente) | Personas | Estado | Condición |
|---|---|---|---|---|
| F01 LAPD NIBRS | no declara | identificables | integrada | solo agregados |
| F03 MyLA311 2026 | Creative Commons 1.0 Universal (Public Domain Dedication) | identificables (dirección) | integrada | solo agregados |
| F04 Permisos LADBS | no declara | identificables (número de predio) | integrada | solo agregados |
| F06 DOF E-1 | no declara | no | integrada | abierto |
| F07 Census ACS 5 años | Términos de la API del Censo (exigen atribución; ver `lago/demografia.json`) | no (conteos agregados) | integrada | llave gratuita en `.env`; mostrar «This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau.» |
| F09 Metro Bike Share | no declara | no | integrada | abierto |
| F10 OpenStreetMap | OpenStreetMap is open data, licensed under the Open Data Commons Open Database License (ODbL) by the OpenStreetMap Foundation (OSMF). | no | integrada | atribución y compartir igual |
| F11 Wikipedia | All Analytics datasets are available under the Creative Commons CC0 dedication. | no | integrada | abierto |
| F12 Distritos de consejo (GeoHub) | no declara | no | integrada | abierto |
| F17 Fotografía de fondo (Wikimedia Commons) | CC BY-SA 4.0 (Alaiben) | no (figuras lejanas) | integrada a la capa web | atribución en el pie; la copia redimensionada se comparte igual |
| F18 Áreas de LAPD (GeoHub) | This data is provided as is with no warranty of any kind. This work is licensed under a Creative Commons Attribution 4.0 International License | no | integrada | atribución en el pie |
| F19 Distritos de reporte de LAPD (GeoHub) | no declara | no | integrada | abierto; las ofensas por distrito llevan supresión |

Las candidatas y descartadas (F02, F05, F08, F13 a F16), con la razón, están en el Excel y en `catalogo/`.

## Despliegue

Proyecto `los-angeles` en Vercel, conectado a este repositorio: cada push a `main` despliega producción (alias `los-angeles-lemon.vercel.app`) y cada pull request tiene su vista previa, protegida con inicio de sesión. `vercel.json` construye con `python3 web/build.py` y publica `web/dist`; `.vercelignore` deja fuera `.env*`, `.vercel/`, `lago/raw/` y `web/dist/`.
