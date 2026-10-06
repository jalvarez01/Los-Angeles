#!/usr/bin/env python3
"""Ingesta F04 · Permisos de construcción emitidos (LADBS) -> lago/vivienda.json

El campo du_changed (cambio en unidades de vivienda) llega como texto: se agrupa en el
servidor por distrito y valor, y la suma se hace aquí después de convertirlo a número.
"""
from _censo import poblacion_por_distrito, por_10mil
from _comun import entre, escribir_lago, mes_anterior, meses_completos, soql

DATASET = "pi9x-tg5x"  # Building and Safety - Building Permits Issued from 2020 to Present (N)
URL = f"https://data.lacity.org/resource/{DATASET}.json"

ini, fin = meses_completos(12)
sini, _ = meses_completos(20)
W = entre("issue_date", ini, fin)
VIG = f"{ini:%Y-%m} a {mes_anterior(fin)}"

total = int(soql(DATASET, select="count(*) AS n", where=W)[0]["n"])
por_cd = {r["cd"]: int(r["n"]) for r in
          soql(DATASET, select="cd, count(*) AS n", where=W, group="cd") if r.get("cd")}
unidades = soql(DATASET, select="cd, du_changed, count(*) AS n",
                where=W + " AND du_changed IS NOT NULL", group="cd, du_changed", limit=50000)
mensual = soql(DATASET, select="date_trunc_ym(issue_date) AS mes, count(*) AS n",
               where=entre("issue_date", sini, fin), group="mes", order="mes")

netas, netas_cd = 0, {}
for r in unidades:
    v = int(float(r["du_changed"])) * int(r["n"])  # texto -> número antes de sumar
    netas += v
    if r.get("cd"):
        netas_cd[r["cd"]] = netas_cd.get(r["cd"], 0) + v

pob = poblacion_por_distrito()
sin_cd = total - sum(por_cd.values())
sin_cd_netas = netas - sum(netas_cd.values())

escribir_lago(
    "vivienda",
    fuentes=[{"id": "F04", "nombre": "Building and Safety - Building Permits Issued from 2020 to Present (N)",
              "url": URL, "estado": "vivo", "licencia": "no declara"}],
    cifras={
        "permisos_12m": {"valor": total, "unidad": "permisos de construcción emitidos",
                         "vigencia": VIG, "fuente": "F04"},
        "unidades_netas_12m": {"valor": netas, "unidad": "unidades de vivienda (neto, según permisos emitidos)",
                               "vigencia": VIG, "fuente": "F04"},
    },
    series={"permisos_mensuales": {"unidad": "permisos de construcción emitidos", "fuente": "F04",
                                   "puntos": [[r["mes"][:7], int(r["n"])] for r in mensual]}},
    tablas={"permisos_por_distrito": {
        "unidad": "permisos emitidos / unidades de vivienda netas (y sus tasas por 10.000 habitantes)", "vigencia": VIG, "fuente": "F04",
        "columnas": ["cd", "permisos", "unidades_netas", "permisos_por_10mil", "unidades_netas_por_10mil"],
        "filas": [[int(cd), por_cd[cd], netas_cd.get(cd, 0), por_10mil(por_cd[cd], cd, pob),
                   por_10mil(netas_cd.get(cd, 0), cd, pob)] for cd in sorted(por_cd, key=int)],
        "nota": f"{sin_cd} permisos del periodo no traen distrito de consejo "
                f"(y {sin_cd_netas} de las unidades netas): quedan fuera de las filas y dentro de los totales. "
                f"Las tasas son por 10.000 habitantes del distrito (población ACS {pob['anio']} de F07, aproximada)"}},
)
