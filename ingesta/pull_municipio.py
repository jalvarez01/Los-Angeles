#!/usr/bin/env python3
"""Ingesta F03 · Solicitudes ciudadanas MyLA311 -> lago/municipio.json

Ojo, ciclo de vida: el portal publica un conjunto por año («MyLA311 Cases 2026»).
En enero hay que cambiar DATASET por el del año nuevo y anotarlo en el catálogo.
"""
import datetime

from _censo import poblacion_por_distrito, por_10mil
from _comun import entre, escribir_lago, hoy, mes_anterior, soql

DATASET = "2cy6-i7zn"  # MyLA311 Cases 2026
ANIO = 2026
URL = f"https://data.lacity.org/resource/{DATASET}.json"
UNIDAD = "solicitudes de servicio"
CERRADAS = ("Closed", "Closed Ext-Referred")
INFORMATIVA = "Information-Only"  # se cierra al instante: infla el % de cerradas

ini = datetime.date(ANIO, 1, 1)
fin = hoy().replace(day=1)
W = entre("createddate", ini, fin)
VIG = f"{ini:%Y-%m} a {mes_anterior(fin)}"

total = int(soql(DATASET, select="count(*) AS n", where=W)[0]["n"])
estados = {r.get("status"): int(r["n"]) for r in
           soql(DATASET, select="status, count(*) AS n", where=W, group="status")}
estados_sin_info = {r.get("status"): int(r["n"]) for r in
                    soql(DATASET, select="status, count(*) AS n", where=W + f" AND type != '{INFORMATIVA}'",
                         group="status")}
total_sin_info = sum(estados_sin_info.values())
tipos = soql(DATASET, select="type, count(*) AS n", where=W, group="type", order="n DESC", limit=10)
distritos = soql(DATASET, select="locator_council_district AS cd, count(*) AS n", where=W, group="cd")
mensual = soql(DATASET, select="date_trunc_ym(createddate) AS mes, count(*) AS n",
               where=W, group="mes", order="mes")

# Las solicitudes sin distrito (vacío o 0) no se inventan: quedan fuera de la tabla y se dicen en la nota
por_cd = sorted(([int(r["cd"]), int(r["n"])] for r in distritos if r.get("cd") not in (None, "", "0")))
sin_cd = total - sum(n for _, n in por_cd)
pob = poblacion_por_distrito()

escribir_lago(
    "municipio",
    fuentes=[{"id": "F03", "nombre": f"MyLA311 Cases {ANIO}", "url": URL,
              "estado": "vivo", "licencia": "Creative Commons 1.0 Universal (Public Domain Dedication)"}],
    cifras={
        "solicitudes_anio": {"valor": total, "unidad": UNIDAD, "vigencia": VIG, "fuente": "F03"},
        "pct_cerradas": {"valor": round(100 * sum(estados.get(s, 0) for s in CERRADAS) / total, 1),
                         "unidad": "% de todas las solicitudes del periodo, incluidas las de tipo Information-Only "
                                   "(que se cierran al instante e inflan el porcentaje)",
                         "vigencia": VIG, "fuente": "F03"},
        "pct_cerradas_sin_informativas": {
            "valor": round(100 * sum(estados_sin_info.get(s, 0) for s in CERRADAS) / total_sin_info, 1),
            "unidad": f"% de las solicitudes del periodo sin contar el tipo {INFORMATIVA} "
                      f"({total_sin_info} de {total} solicitudes)",
            "vigencia": VIG, "fuente": "F03"},
    },
    series={"solicitudes_mensuales": {"unidad": UNIDAD, "fuente": "F03",
                                      "puntos": [[r["mes"][:7], int(r["n"])] for r in mensual]}},
    tablas={
        "solicitudes_por_tipo": {"unidad": UNIDAD, "vigencia": VIG, "fuente": "F03",
                                 "columnas": ["tipo", "solicitudes"],
                                 "filas": [[r["type"], int(r["n"])] for r in tipos]},
        "solicitudes_por_distrito": {"unidad": UNIDAD + " (y solicitudes por 10.000 habitantes)", "vigencia": VIG, "fuente": "F03",
                                     "columnas": ["cd", "solicitudes", "solicitudes_por_10mil"],
                                     "filas": [[cd, n, por_10mil(n, cd, pob)] for cd, n in por_cd],
                                     "nota": f"{sin_cd} solicitudes del periodo no traen distrito de consejo. "
                                             f"La tasa es solicitudes del periodo por 10.000 habitantes del distrito "
                                             f"(población ACS {pob['anio']} de F07, aproximada: ver demografia.json)"},
    },
)
