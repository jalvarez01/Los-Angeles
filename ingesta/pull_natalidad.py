#!/usr/bin/env python3
"""Ingesta F07 · Natalidad y población por distrito (Censo de EE. UU., ACS de 5 años) -> lago/demografia.json

Natalidad: de B13016 (mujeres de 15 a 50 años y las que tuvieron un nacimiento en los últimos 12 meses) se
calculan nacimientos por 1.000 mujeres de 15 a 50 años, para la ciudad (place 06-44000), California y EE. UU.,
en el último lanzamiento disponible, y para la ciudad en todos los lanzamientos que responden.
Población por distrito: B01003 por sector censal del condado de Los Ángeles, asignado a cada distrito de
consejo por el punto interno del sector (ver _censo.py). Ningún dato individual llega al lago.
Necesita CENSUS_API_KEY en .env. Se funde con lo que F06 ya escribió en demografia.json.
"""
from _censo import api, lanzamientos, poblacion_por_distrito
from _comun import escribir_lago

URL = "https://api.census.gov/data/{anio}/acs/acs5"
# Texto copiado de https://www.census.gov/data/developers/about/terms-of-service.html (consultado el día de la ingesta)
LICENCIA = ('Census Bureau API Terms of Service (census.gov/data/developers/about/terms-of-service.html): '
            '"You may use the Census Bureau API to develop a service or service to search, display, analyze, '
            'retrieve, view and otherwise \"get\" information from Census Bureau data." Atribución exigida: '
            '"This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau."')
VARS = ["B13016_001E", "B13016_002E"]
AMBITOS = [("Ciudad de Los Ángeles", "place:44000", ["state:06"]),
           ("California", "state:06", None),
           ("Estados Unidos", "us:1", None)]

anios = lanzamientos()
ultimo = anios[-1]
periodo = lambda a: f"{a - 4}-{a}"
tasa = lambda mujeres, nac: round(1000 * nac / mujeres, 1)
miles = lambda n: f"{n:,}".replace(",", ".")  # 3.848.338, como en el resto del proyecto

filas, ciudad = [], None
for nombre, para, en in AMBITOS:
    m, n = (int(x) for x in api(ultimo, VARS, para, en)[0][:2])
    filas.append([nombre, m, n, tasa(m, n)])
ciudad = filas[0]
serie = []
for a in anios:
    m, n = (int(x) for x in api(a, VARS, "place:44000", ["state:06"])[0][:2])
    serie.append([periodo(a), m, n, tasa(m, n)])

pob = poblacion_por_distrito()
total_asignado = sum(pob["poblacion"].values())
dif = total_asignado - pob['poblacion_ciudad_acs']
nota_pob = (
    f"Método: se suman los {miles(sum(pob['sectores'].values()))} sectores censales del condado de Los Ángeles (ACS {pob['anio']}, "
    "B01003_001E) cuyo punto interno (Gazetteer del Censo 2020) cae dentro de cada distrito, usando los límites "
    "completos de F12 (sin simplificar). Error: un sector que cruza el límite de dos distritos se asigna entero al "
    "distrito de su punto interno, así que cada distrito puede quedar algo por encima o por debajo; el error por "
    "distrito no se puede medir con esta fuente. A escala de ciudad, la suma de los distritos "
    f"({miles(total_asignado)}) difiere {'+' if dif >= 0 else '-'}{miles(abs(dif))} habitantes ({100 * dif / pob['poblacion_ciudad_acs']:+.2f} %) de la "
    f"población de la ciudad en el mismo ACS ({miles(pob['poblacion_ciudad_acs'])}). "
    "Son estimaciones de encuesta con margen de error, no un censo."
)

V = f"ACS {periodo(ultimo)}"
escribir_lago(
    "demografia",
    fuentes=[{"id": "F07", "nombre": "American Community Survey 5-Year Estimates (API)",
              "url": URL.format(anio=ultimo), "estado": "vivo",
              "licencia": LICENCIA}],
    cifras={
        "natalidad_ciudad_por_1000": {
            "valor": ciudad[3], "unidad": "nacimientos en los últimos 12 meses por 1.000 mujeres de 15 a 50 años",
            "vigencia": V, "fuente": "F07"},
    },
    tablas={
        "natalidad_por_ambito": {
            "unidad": "mujeres de 15 a 50 años; nacimientos en los últimos 12 meses; nacimientos por 1.000 mujeres",
            "vigencia": V, "fuente": "F07",
            "columnas": ["ambito", "mujeres_15_50", "nacimientos", "nacimientos_por_1000"], "filas": filas,
            "nota": "B13016_002E / B13016_001E × 1.000. Estimaciones del ACS con margen de error."},
        "natalidad_serie_ciudad": {
            "unidad": "mujeres de 15 a 50 años; nacimientos en los últimos 12 meses; nacimientos por 1.000 mujeres",
            "vigencia": f"{periodo(anios[0])} a {periodo(ultimo)}", "fuente": "F07",
            "columnas": ["periodo", "mujeres_15_50", "nacimientos", "nacimientos_por_1000"], "filas": serie,
            "nota": "Una fila por lanzamiento del ACS de 5 años (el periodo es la ventana de 5 años). Los lanzamientos "
                    "consecutivos se traslapan (comparten cuatro de sus cinco años), así que los puntos consecutivos no "
                    "son independientes y no deben compararse entre sí. Solo se deben comparar ventanas que no se "
                    "traslapen: 2006-2010, 2011-2015, 2016-2020 y 2020-2024 (las dos últimas comparten únicamente el año 2020)."},
        "poblacion_por_distrito": {
            "unidad": "habitantes", "vigencia": V, "fuente": "F07",
            "columnas": ["cd", "poblacion", "sectores_censales"],
            "filas": [[int(cd), pob["poblacion"][cd], pob["sectores"][cd]] for cd in pob["poblacion"]],
            "nota": nota_pob},
    },
    fusionar=True,
)
