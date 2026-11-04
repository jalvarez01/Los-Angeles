#!/usr/bin/env python3
"""Ingesta F07 · Natalidad y población por distrito (Censo de EE. UU., ACS de 5 años) -> lago/demografia.json

Natalidad: de B13016 (mujeres de 15 a 50 años y las que tuvieron un nacimiento en los últimos 12 meses) se
calculan nacimientos por 1.000 mujeres de 15 a 50 años, para la ciudad (place 06-44000), California y EE. UU.,
en el último lanzamiento disponible, y para la ciudad en todos los lanzamientos que responden.
Población y natalidad por distrito: B01003 y B13016 por sector censal del condado de Los Ángeles, asignados a cada
distrito de consejo por el punto interno del sector (ver _censo.py). Ningún dato individual llega al lago.
Necesita CENSUS_API_KEY en .env. Se funde con lo que F06 ya escribió en demografia.json.
"""
from _censo import (LICENCIA, NOTA_MOE, api, lanzamientos, moe_proporcion, poblacion_por_distrito, poligonos_distritos,
                    significativa, suma_por_poligono, valor)
from _comun import escribir_lago

URL = "https://api.census.gov/data/{anio}/acs/acs5"
VARS = ["B13016_001E", "B13016_002E", "B13016_001M", "B13016_002M"]  # estimación y MOE de mujeres y nacimientos
AMBITOS = [("Ciudad de Los Ángeles", "place:44000", ["state:06"]),
           ("California", "state:06", None),
           ("Estados Unidos", "us:1", None)]

anios = lanzamientos()
ultimo = anios[-1]
periodo = lambda a: f"{a - 4}-{a}"
tasa = lambda mujeres, nac: round(1000 * nac / mujeres, 1)
miles = lambda n: f"{n:,}".replace(",", ".")  # 3.848.338, como en el resto del proyecto
COLS = ["mujeres_15_50", "nacimientos", "nacimientos_por_1000",
        "mujeres_15_50_moe", "nacimientos_moe", "nacimientos_por_1000_moe"]
formulas = {}  # tabla -> {fórmula: veces}


def fila(tabla, clave, m, n, mm, mn):
    """[clave, mujeres, nacimientos, tasa, MOE mujeres, MOE nacimientos, MOE tasa] (tasa por 1.000, MOE al 90 %)."""
    moe_p, formula = moe_proporcion(m, n, mm, mn)
    formulas.setdefault(tabla, {}).setdefault(formula, 0)
    formulas[tabla][formula] += 1
    return [clave, m, n, tasa(m, n), round(mm), round(mn), round(1000 * moe_p, 1)]


def lee(anio, para, en):
    return [valor(v, x) for v, x in zip(VARS, api(anio, VARS, para, en)[0])]


filas = [fila("natalidad_por_ambito", nombre, *lee(ultimo, para, en)) for nombre, para, en in AMBITOS]
ciudad = filas[0]
serie = [fila("natalidad_serie_ciudad", periodo(a), *lee(a, "place:44000", ["state:06"])) for a in anios]
nota_formula = lambda t: ("MOE de la tasa con la fórmula de proporción del Census Bureau, MOE_p = (1/X)·raíz(MOE_Y² − "
                          "p²·MOE_X²), con X = mujeres e Y = nacimientos; si el radicando es negativo se usa la de razón "
                          "(con +). Aquí: " + ", ".join(f"{k} en {v}" for k, v in formulas[t].items()) + ".")

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

# Natalidad por distrito: mismos sectores y mismo lanzamiento que la cifra de la ciudad
nd = suma_por_poligono(ultimo, VARS, poligonos_distritos())
filas_cd = [fila("natalidad_por_distrito", cd, *v) for cd, v in sorted(nd["suma"].items())]
filas_cd = [f + [significativa(f[3], f[6], ciudad[3], ciudad[6])] for f in filas_cd]
sm, sn = sum(f[1] for f in filas_cd), sum(f[2] for f in filas_cd)
pct = lambda a, b: f"{100 * (a - b) / b:+.2f} %"
nota_nat = (
    f"Método: B13016_001E (mujeres de 15 a 50 años) y B13016_002E (las que tuvieron un nacimiento en los últimos "
    f"12 meses) de los {miles(sum(nd['sectores'].values()))} sectores censales del condado (ACS {periodo(ultimo)}) "
    "cuyo punto interno cae en cada distrito, con los límites completos de F12; la tasa es nacimientos / mujeres × 1.000. "
    "Error: un sector que cruza el límite de dos distritos se asigna entero al de su punto interno, y a esta escala el "
    "margen de error del ACS es grande (pocas mujeres con nacimiento por sector), así que diferencias pequeñas entre "
    f"distritos no son significativas. A escala de ciudad, la suma de los distritos ({miles(sm)} mujeres, {miles(sn)} "
    f"nacimientos) difiere {pct(sm, ciudad[1])} y {pct(sn, ciudad[2])} de las cifras de la ciudad en el mismo ACS "
    f"({miles(ciudad[1])} y {miles(ciudad[2])}).")
escribir_lago(
    "demografia",
    fuentes=[{"id": "F07", "nombre": "American Community Survey 5-Year Estimates (API)",
              "url": URL.format(anio=ultimo), "estado": "vivo",
              "licencia": LICENCIA}],
    cifras={
        "natalidad_ciudad_por_1000": {
            "valor": ciudad[3], "moe": ciudad[6],
            "unidad": "nacimientos en los últimos 12 meses por 1.000 mujeres de 15 a 50 años (± MOE al 90 %)",
            "vigencia": V, "fuente": "F07"},
    },
    tablas={
        "natalidad_por_ambito": {
            "unidad": "mujeres de 15 a 50 años; nacimientos en los últimos 12 meses; nacimientos por 1.000 mujeres",
            "vigencia": V, "fuente": "F07",
            "columnas": ["ambito", *COLS], "filas": filas,
            "nota": "B13016_002E / B13016_001E × 1.000. Estimaciones del ACS con margen de error. "
                    + nota_formula("natalidad_por_ambito")},
        "natalidad_serie_ciudad": {
            "unidad": "mujeres de 15 a 50 años; nacimientos en los últimos 12 meses; nacimientos por 1.000 mujeres",
            "vigencia": f"{periodo(anios[0])} a {periodo(ultimo)}", "fuente": "F07",
            "columnas": ["periodo", *COLS], "filas": serie, "nota_moe": nota_formula("natalidad_serie_ciudad"),
            "nota": "Una fila por lanzamiento del ACS de 5 años (el periodo es la ventana de 5 años). Los lanzamientos "
                    "consecutivos se traslapan (comparten cuatro de sus cinco años), así que los puntos consecutivos no "
                    "son independientes y no deben compararse entre sí. Solo se deben comparar ventanas que no se "
                    "traslapen: 2010-2014, 2015-2019 y 2020-2024."},
        "poblacion_por_distrito": {
            "unidad": "habitantes", "vigencia": V, "fuente": "F07",
            "columnas": ["cd", "poblacion", "sectores_censales", "poblacion_moe"],
            "filas": [[int(cd), pob["poblacion"][cd], pob["sectores"][cd], pob["poblacion_moe"][cd]] for cd in pob["poblacion"]],
            "referencia_ciudad": {"poblacion": sum(pob["poblacion"].values()),
                                  "poblacion_moe": round(sum(m ** 2 for m in pob["poblacion_moe"].values()) ** .5)},
            "nota": nota_pob, "nota_moe": NOTA_MOE},
        "natalidad_por_distrito": {
            "unidad": "mujeres de 15 a 50 años; nacimientos en los últimos 12 meses; nacimientos por 1.000 mujeres",
            "vigencia": V, "fuente": "F07",
            "columnas": ["cd", *COLS, "nacimientos_por_1000_dif_significativa"], "filas": filas_cd,
            "referencia_ciudad": {"nacimientos_por_1000": [ciudad[3], ciudad[6]]},
            "nota": nota_nat,
            "nota_moe": NOTA_MOE.split(" Una tasa con numerador exacto")[0] + " " + nota_formula("natalidad_por_distrito")
                        + " La columna _dif_significativa compara cada distrito con la ciudad (place 06-44000, mismo "
                          "ACS) con la prueba del Census Bureau a 90 %: |r − r_ciudad| / raíz(EE² + EE_ciudad²) > 1,645, "
                          "EE = MOE / 1,645."},
    },
    fusionar=True,
)
