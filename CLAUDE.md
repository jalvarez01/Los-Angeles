# CLAUDE.md · Los Ángeles · sistema de información

Contexto para continuar el trabajo sin el historial del chat. El detalle está en `README.md`; aquí van las reglas.

## Qué es

Trabajo de curso (Sexto Semestre) de Jeronimo Escobar Restrepo y Juan Jose Alvarez Ocampo. Un «lago» de datos abiertos
de la ciudad de Los Ángeles y una web estática que lo muestra.

- **Usuario:** un concejal del Ayuntamiento y su equipo. **Escala:** la ciudad y sus 15 distritos de consejo
  (LAPD reporta por 21 áreas propias que no coinciden con los distritos).
- **Preguntas:** dónde se concentran los delitos; qué piden los vecinos por 311 y cuánto se resuelve; dónde se
  construye y cuánta vivienda se suma; contexto (población, movilidad, equipamientos, interés externo).
- Repo: github.com/jalvarez01/Los-Angeles (colaboradores: `jalvarez01` admin, `jeronimoescobar` write).
  Sitio: https://los-angeles-lemon.vercel.app

## Estructura

| Ruta | Qué es |
|---|---|
| `ingesta/pull_*.py` | un script por tema; `_comun.py` (HTTP, SoQL, escritura), `_censo.py` (API del Censo) |
| `lago/*.json` | siete temas con el contrato; `lago/raw/` es intermedio e ignorado por git |
| `territorio/distritos_consejo.geojson` | 15 distritos, simplificados (~300 m) |
| `verificacion/verificar.py` | comprueba contrato, sumas, rangos y antigüedad; debe dar `0 fallos` |
| `catalogo/fuentes.py` → `catalogo/F*.json` | fuente única de las fichas; las fichas se regeneran, no se editan a mano |
| `web/index.html`, `web/assets/`, `web/build.py` | web estática; `build.py` arma `web/dist/` (ignorado) con el lago copiado |
| `entrega1/` | `Diccionario_de_datos_LosAngeles.xlsx` y `LosAngeles.docx` (entregables; no tocar sin pedirlo) |

## Comandos

```
# reconstruir el lago (red; ~4 min; cifras cambian en cada corrida)
rm -rf lago territorio
for s in ingesta/pull_*.py; do python3 "$s"; done
python3 verificacion/verificar.py          # debe terminar en "0 fallos"
git diff --stat -- lago/ territorio/

python3 catalogo/fuentes.py                # regenera catalogo/F*.json
python3 web/build.py && python3 -m http.server -d web/dist   # probar la web
```

Para auditar sin tocar el repo, reconstruir en una copia (`cp -r` a un directorio temporal).

## Contrato del lago

Cada tema: `tema`, `probado` (AAAA-MM-DD), `fuentes` (id, url, licencia), `cifras` (cada una con `valor`, `unidad`,
`vigencia`, `fuente`), `series` (meses AAAA-MM ordenados, sin repetir) y nuestra extensión `tablas` (`unidad`,
`vigencia`, `fuente`, `columnas`, `filas`). Los conteos se calculan en el servidor de cada fuente.

## Reglas duras

- Solo biblioteca estándar de Python (3.10+). Nada de pip.
- Ningún registro individual llega al lago ni a la web (delitos, solicitudes 311, permisos: ni ubicaciones, ni número
  de predio, ni marcas de violencia doméstica). Solo agregados.
- `CENSUS_API_KEY` vive en `.env` (ignorado). Nunca imprimirla, copiarla a otro archivo, ni subirla. La web no hace
  llamadas en vivo.
- Mostrar en la web la atribución del Censo: «This product uses the Census Bureau Data API but is not endorsed or
  certified by the Census Bureau.»
- **Imágenes de fondo:** solo con licencia libre verificada en la página de origen, con autor, licencia, URL, tamaño
  en px y bytes registrados en `catalogo/fuentes.py` (y regenerado), en el README y en el pie de `web/index.html`.
  Nunca imágenes sacadas de buscadores sin autor conocido.
- Preguntar antes de cada commit, push, PR o despliegue.

## Fuentes

| ID | Fuente | Estado |
|---|---|---|
| F01 | LAPD NIBRS Offenses | integrada (solo agregados) |
| F03 | MyLA311 Cases 2026 (`2cy6-i7zn`) | integrada (solo agregados) |
| F04 | LADBS Building Permits (`pi9x-tg5x`) | integrada (solo agregados) |
| F06 | DOF E-1 | integrada |
| F07 | Census ACS 5 años (API, llave) | integrada (solo agregados) |
| F09 | Metro Bike Share GBFS | integrada |
| F10 | OpenStreetMap vía Overpass | integrada (ODbL: atribución) |
| F11 | Vistas de Wikipedia | integrada |
| F12 | Distritos de consejo (GeoHub) | integrada |
| F17 | Foto de fondo, Alaiben, CC BY-SA 4.0 (Wikimedia Commons) | integrada a la web, no al lago |
| F02, F05, F08, F13, F14, F16 | — | descartadas |
| F15 | «Transport for Los Angeles API» | no existe (la inventó la IA) |

## Despliegue (Vercel)

- Proyecto `los-angeles` (equipo de `jalvarez01`), enlazado en `.vercel/` (ignorado). `vercel.json`: build
  `python3 web/build.py`, salida `web/dist`. `.vercelignore` excluye `.env*`, `.vercel/`, `lago/raw/`, `web/dist/`.
- Producción: alias `los-angeles-lemon.vercel.app`. Las vistas previas están protegidas con inicio de sesión.
- Sin despliegue automático desde Git: se despliega a mano con `npx vercel` (vista previa) o `npx vercel --prod`.
  Producción no se actualiza al hacer push.
- Tras desplegar: `/` da 200 y `/.env` da 404.

## Rarezas conocidas

- Overpass (F10) a veces responde 504 o tarda ~1 min; reintentar más tarde.
- MyLA311 publica un conjunto por año: cada enero hay que cambiar `DATASET` en `ingesta/pull_municipio.py` y
  anotarlo en el catálogo.
- LAPD carga con semanas de rezago: la ventana de seguridad termina en el último mes completo de la fuente.
  Municipio y vivienda también cuentan solo meses completos.
- Excel, hoja `Resumen`: las fórmulas usan rangos fijos (filas 5 a 100 de las otras hojas; la fila 4 es el
  ejemplo y queda fuera). Una fila fuera de ese rango no se cuenta. Las fórmulas no guardan valores, así que los
  visores que no recalculan las muestran vacías.

## Git

- Commits solo como `jalvarez01 <juanjosealvarezag@gmail.com>`; mensajes cortos, en español, en minúscula, uno por
  paso lógico. Sin `Co-Authored-By` ni menciones a Claude, IA o Anthropic.
- Trabajar en rama; `git pull --ff-only` en `main` antes de empezar. No hacer push, PR ni desplegar sin permiso.
