# Los Ángeles · Sistema de Información

- Jeronimo Escobar Restrepo · Juan Jose Alvarez Ocampo 
- Sitio: https://los-angeles-lemon.vercel.app

## Entrega 1 · el lago y su diccionario

- `entrega1/Diccionario_de_datos_LosAngeles.xlsx` — 18 fuentes (F01–F16, F18 y F19; la foto F17 solo está en `catalogo/`), 95 campos y la bitácora de la búsqueda.
- `entrega1/LosAngeles.docx` — las seis respuestas. Sus cifras corresponden al lago construido el 2026-10-06; el lago se ha reconstruido desde entonces, así que las cifras actuales no coinciden con las del Word.
- `catalogo/` — una ficha por fuente (`F01.json` … `F19.json`), generadas desde `catalogo/fuentes.py`.
- `lago/` — siete temas con la forma del contrato. `territorio/` — los 15 distritos de consejo, las 21 áreas de LAPD y sus 1.135 distritos de reporte.

## Cómo se reconstruye

```
rm -rf lago territorio
for s in ingesta/pull_*.py; do python3 "$s"; done
python3 verificacion/verificar.py
git diff --stat -- lago/ territorio/
```

Solo biblioteca estándar de Python (3.10 o más). Una sola llave: `CENSUS_API_KEY` (gratuita, en https://api.census.gov/data/key_signup.html) en un archivo `.env` en la raíz, que está en `.gitignore` y nunca se sube; sin ella se detienen con un aviso `ingesta/pull_natalidad.py`, `pull_seguridad.py` y `pull_equipamientos.py` (los tres usan población del Censo). Overpass (F10) a veces responde 502 o 504: `pull_equipamientos.py` reintenta solo, y si aun así falla se vuelve a correr ese script; `verificar.py` falla si falta algún tema. El lago de esta entrega se construyó el 2026-10-05 y
la verificación terminó con 0 fallos. Las cifras cambian cada vez que se reconstruye: las fuentes siguen cargando datos.

## El lago

| Archivo | Fuente | Qué trae |
|---|---|---|
| `lago/seguridad.json` | F01, F07, F18, F19 | ofensas NIBRS de los últimos 12 meses completos de la fuente, por categoría (personas, propiedad, sociedad, varias y sin categoría: suman el total), por mes, por área de LAPD (con población del ACS y ofensas por 10.000 habitantes) y por distrito de reporte (celdas con menos de 10 suprimidas) |
| `lago/municipio.json` | F03 | solicitudes 311 del año, % cerradas (con y sin el tipo Information-Only), por tipo, distrito (con tasa por 10.000 habitantes) y mes |
| `lago/vivienda.json` | F04 | permisos de construcción y unidades netas, por distrito (con tasas por 10.000 habitantes y la nota de los que no traen distrito) y mes |
| `lago/demografia.json` | F06 y F07 | población y viviendas de la ciudad al 1 de enero (F06); natalidad de la ciudad, California y EE. UU., serie anual de la ciudad, población y natalidad por distrito de consejo (F07) |
| `lago/movilidad.json` | F09 | bicicleta compartida en tiempo real y las estaciones con nombre, coordenadas, bicis y anclajes |
| `lago/equipamientos.json` | F10, F12, F07 | hoteles, hospitales, colegios y parques en OpenStreetMap; colegios, hospitales y parques por distrito (conteo y por 10.000 habitantes, sin coordenadas) |
| `lago/escucha.json` | F11 | vistas del artículo «Los Ángeles» en Wikipedia |
| `territorio/distritos_consejo.geojson` | F12 | límites de los 15 distritos, simplificados (~300 m), con vigencia de los nombres |
| `territorio/areas_lapd.geojson` | F18 | límites de las 21 áreas de LAPD, simplificados (~300 m) |
| `territorio/distritos_reporte_lapd.geojson` | F19 | límites de los 1.135 distritos de reporte de LAPD, simplificados (~50 m) |

Contrato: el de Lima (`tema`, `probado`, `fuentes`, `cifras`, `series`) más una extensión nuestra, `tablas`, para
los desgloses por zona: cada tabla lleva `unidad`, `vigencia`, `fuente`, `columnas` y `filas`, y la verificación
las comprueba. Ningún registro individual llega al lago: los conteos se calculan en el servidor de cada fuente.

LAPD carga los delitos con unas semanas de rezago, así que la ventana de seguridad termina en el último mes completo
que tiene la fuente, no en el del calendario.

Regla de supresión (seguridad por distrito de reporte): toda celda con 1 a 9 ofensas se guarda como `null` con `suprimido = true`, nunca el número; si en un área queda una sola celda suprimida se suprime también la visible más pequeña, para que no se despeje restando del total del área. La verificación falla si algún conteo guardado está entre 1 y 9.

## Capa web

Publicada en https://los-angeles-lemon.vercel.app (producción; las vistas previas de Vercel quedan protegidas con inicio de sesión). `web/` es un sitio estático que lee solo `lago/` y `territorio/` (sin llamadas en vivo; la llave del Censo nunca llega al navegador). Se prueba con `python3 web/build.py && python3 -m http.server -d web/dist`; `build.py` copia el lago al sitio.

Mapas (Leaflet, sin teselas externas: solo la geometría de `territorio/`; cada uno con leyenda por quintiles, tooltip, fuente y vigencia debajo y un selector):

1. Seguridad · ofensas por área de LAPD: total o por 10.000 habitantes (F01, F18, F07).
2. Seguridad · ofensas por distrito de reporte, con las celdas suprimidas rayadas y un selector para acercar a cada área (F01, F19).
3. Distritos de consejo · 311, permisos, población, natalidad por 1.000 mujeres de 15 a 50 años, y colegios, hospitales y parques (conteo y por 10.000 habitantes) (F03, F04, F07, F10, F12).
4. Movilidad · estaciones de Metro Bike Share sobre los distritos, con el tamaño según bicis disponibles o anclajes libres (F09, F12).

Diseño: inspirado en los menús de pausa de los videojuegos de mundo abierto, sin ningún recurso de terceros del juego; tipografías Anton e IBM Plex Sans (Google Fonts). Fotografía de fondo: «Echo park lake with lotus flowers and Los Angeles skyline in the background», de Alaiben, CC BY-SA 4.0, vía [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Echo_park_lake_with_lotus_flowers_and_Los_Angeles_skyline_in_the_background.jpg) (F17, en `web/assets/fondo-los-angeles.jpg`, 2400 × 1515 px y 452.634 bytes; la gradación de color es solo CSS).

## Para quién y qué pregunta

- **Usuario:** un concejal del Ayuntamiento y su equipo.
- **Preguntas:** ¿dónde se concentran los delitos y cómo evolucionan? · ¿qué piden los vecinos, en qué distritos y cuánto se resuelve? · ¿dónde se construye y cuánta vivienda se suma? · contexto: población, movilidad, equipamientos, interés externo.
- **Escala:** la ciudad y sus 15 distritos de consejo. LAPD reporta por 21 áreas propias que no coinciden con los distritos.
- **Lo que decidimos no mostrar:** ningún registro individual de delitos, solicitudes 311 ni permisos (ubicaciones, número de predio, marcas de violencia doméstica).

## ¿Se puede usar?

| Fuente | Licencia | Personas | Estado | Condición |
|---|---|---|---|---|
| F01 LAPD NIBRS | no declara | identificables | integrada | solo agregados |
| F03 MyLA311 2026 | CC0 | identificables (dirección) | integrada | solo agregados |
| F04 Permisos LADBS | no declara | identificables (número de predio) | integrada | solo agregados |
| F06 DOF E-1 | no declara | no | integrada | abierto |
| F07 Census ACS 5 años | Términos de la API del Censo (exigen atribución; ver `lago/demografia.json`) | no (conteos agregados) | integrada | llave gratuita en `.env`; mostrar «This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau.» |
| F17 Fotografía de fondo (Wikimedia Commons) | CC BY-SA 4.0 (Alaiben) | no (figuras lejanas) | integrada a la capa web | atribución en el pie de la web; la copia redimensionada se comparte igual |
| F09 Metro Bike Share | no declara | no | integrada | abierto |
| F10 OpenStreetMap | ODbL | no | integrada | atribución y compartir igual |
| F11 Wikipedia | CC0 | no | integrada | abierto |
| F12 Distritos (GeoHub) | no declara | no | integrada | abierto |
| F18 Áreas de LAPD (GeoHub) | CC BY 4.0 («This work is licensed under a Creative Commons Attribution 4.0 International License») | no | integrada | atribución en el pie de la web |
| F19 Distritos de reporte de LAPD (GeoHub) | no declara | no | integrada | abierto; las ofensas por distrito llevan supresión de celdas con menos de 10 |

Las candidatas y descartadas (F02, F05, F08, F13–F16), con la razón, están en el Excel y en `catalogo/`.
