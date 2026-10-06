# Los Ángeles · sistema de información

Grupo: Jeronimo Escobar Restrepo · Juan Jose Alvarez Ocampo · Repositorio: https://github.com/jalvarez01/Los-Angeles · Revisado: 2026-10-05

## Entrega 1 · el lago y su diccionario

- `entrega1/Diccionario_de_datos_LosAngeles.xlsx` — 16 fuentes, 62 campos y la bitácora de la búsqueda.
- `entrega1/Preguntas_por_que_estos_datos_LosAngeles.docx` — las seis respuestas.
- `catalogo/` — una ficha por fuente (`F01.json` … `F16.json`), generadas desde `catalogo/fuentes.py`.
- `lago/` — siete temas con la forma del contrato. `territorio/` — los 15 distritos de consejo.

## Cómo se reconstruye

```
rm -rf lago territorio
for s in ingesta/pull_*.py; do python3 "$s"; done
python3 verificacion/verificar.py
git diff --stat -- lago/ territorio/
```

Solo biblioteca estándar de Python (3.10 o más). Una sola llave: `CENSUS_API_KEY` (gratuita, en https://api.census.gov/data/key_signup.html) en un archivo `.env` en la raíz, que está en `.gitignore` y nunca se sube; sin ella `ingesta/pull_natalidad.py` se detiene con un aviso. El lago de esta entrega se construyó el 2026-10-05 y
la verificación terminó con 0 fallos. Las cifras cambian cada vez que se reconstruye: las fuentes siguen cargando datos.

## El lago

| Archivo | Fuente | Qué trae |
|---|---|---|
| `lago/seguridad.json` | F01 | ofensas NIBRS de los últimos 12 meses completos de la fuente, por categoría (personas, propiedad, sociedad, varias y sin categoría: suman el total), por área de LAPD y por mes |
| `lago/municipio.json` | F03 | solicitudes 311 del año, % cerradas (con y sin el tipo Information-Only), por tipo, distrito (con tasa por 10.000 habitantes) y mes |
| `lago/vivienda.json` | F04 | permisos de construcción y unidades netas, por distrito (con tasas por 10.000 habitantes y la nota de los que no traen distrito) y mes |
| `lago/demografia.json` | F06 y F07 | población y viviendas de la ciudad al 1 de enero (F06); natalidad de la ciudad, California y EE. UU., serie anual de la ciudad y población por distrito de consejo (F07) |
| `lago/movilidad.json` | F09 | bicicleta compartida en tiempo real |
| `lago/equipamientos.json` | F10 | hoteles, hospitales, colegios y parques en OpenStreetMap |
| `lago/escucha.json` | F11 | vistas del artículo «Los Ángeles» en Wikipedia |
| `territorio/distritos_consejo.geojson` | F12 | límites de los 15 distritos, simplificados (~300 m), con vigencia de los nombres |

Contrato: el de Lima (`tema`, `probado`, `fuentes`, `cifras`, `series`) más una extensión nuestra, `tablas`, para
los desgloses por zona: cada tabla lleva `unidad`, `vigencia`, `fuente`, `columnas` y `filas`, y la verificación
las comprueba. Ningún registro individual llega al lago: los conteos se calculan en el servidor de cada fuente.

LAPD carga los delitos con unas semanas de rezago, así que la ventana de seguridad termina en el último mes completo
que tiene la fuente, no en el del calendario.

## Capa web

`web/` es un sitio estático que lee solo `lago/` y `territorio/` (sin llamadas en vivo; la llave del Censo nunca llega al navegador). Se prueba con `python3 web/build.py && python3 -m http.server -d web/dist`; `build.py` copia el lago al sitio.

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
| F09 Metro Bike Share | no declara | no | integrada | abierto |
| F10 OpenStreetMap | ODbL | no | integrada | atribución y compartir igual |
| F11 Wikipedia | CC0 | no | integrada | abierto |
| F12 Distritos (GeoHub) | no declara | no | integrada | abierto |

Las candidatas y descartadas (F02, F05, F08, F13–F16), con la razón, están en el Excel y en `catalogo/`.
