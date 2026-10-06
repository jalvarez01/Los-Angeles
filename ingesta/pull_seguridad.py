#!/usr/bin/env python3
"""Ingesta F01 · Ofensas registradas por LAPD (NIBRS) -> lago/seguridad.json

Solo se bajan conteos agregados por área y por mes: el registro individual
(dirección por cuadra, hora, marcas de violencia doméstica) nunca llega al lago.
"""
import datetime

from _comun import entre, escribir_lago, hoy, mes_anterior, meses_completos, soql

DATASET = "k7nn-b2ep"  # LAPD NIBRS Offenses Dataset
URL = f"https://data.lacity.org/resource/{DATASET}.json"
UNIDAD = "ofensas registradas (NIBRS)"

# LAPD carga con rezago: el mes en que cae el último hecho registrado está incompleto.
# La ventana termina en el último mes completo que tiene la fuente, no en el del calendario.
ultimo = soql(DATASET, select="max(date_occ) AS m", where=f"date_occ <= '{hoy()}T23:59:59'")[0]["m"]
ref = datetime.date.fromisoformat(ultimo[:10])
ini, fin = meses_completos(12, ref)
sini, _ = meses_completos(20, ref)
W = entre("date_occ", ini, fin)
VIG = f"{ini:%Y-%m} a {mes_anterior(fin)}"

total = int(soql(DATASET, select="count(*) AS n", where=W)[0]["n"])
contra = {r.get("crime_against"): int(r["n"]) for r in
          soql(DATASET, select="crime_against, count(*) AS n", where=W, group="crime_against")}
areas = soql(DATASET, select="area_name, count(*) AS n", where=W, group="area_name", order="n DESC")
mensual = soql(DATASET, select="date_trunc_ym(date_occ) AS mes, count(*) AS n",
               where=entre("date_occ", sini, fin), group="mes", order="mes")

# Las partes deben sumar el total: lo que no es Person/Property/Society (varias categorías a la vez) o viene vacío
# se declara aparte en vez de perderse
BASE = ("Person", "Property", "Society")
varias = sum(n for k, n in contra.items() if k is not None and k not in BASE)
sin_categoria = contra.get(None, 0)

c = lambda v: {"valor": v, "unidad": UNIDAD, "vigencia": VIG, "fuente": "F01"}
escribir_lago(
    "seguridad",
    fuentes=[{"id": "F01", "nombre": "LAPD NIBRS Offenses Dataset", "url": URL,
              "estado": "vivo", "licencia": "no declara"}],
    cifras={
        "delitos_12m": c(total),
        "delitos_contra_personas_12m": c(contra.get("Person", 0)),
        "delitos_contra_propiedad_12m": c(contra.get("Property", 0)),
        "delitos_contra_sociedad_12m": c(contra.get("Society", 0)),
        "delitos_varias_categorias_12m": {
            **c(varias), "unidad": UNIDAD + " clasificadas por la fuente en varias categorías a la vez "
                                            "(p. ej. «Person, Property, Society»)"},
        "delitos_sin_categoria_12m": {
            **c(sin_categoria), "unidad": UNIDAD + " sin categoría (crime_against vacío en la fuente)"},
    },
    series={"delitos_mensuales": {"unidad": UNIDAD, "fuente": "F01",
                                  "puntos": [[r["mes"][:7], int(r["n"])] for r in mensual]}},
    tablas={"delitos_por_area": {"unidad": UNIDAD, "vigencia": VIG, "fuente": "F01",
                                 "columnas": ["area_nombre", "delitos_12m"],
                                 "filas": [[r["area_name"].strip(), int(r["n"])] for r in areas]}},
)
