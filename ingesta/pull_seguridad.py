#!/usr/bin/env python3
"""Ingesta F01 · Ofensas registradas por LAPD (NIBRS) -> lago/seguridad.json
y F18 · Áreas de LAPD (LA GeoHub) -> territorio/areas_lapd.geojson

Solo se bajan conteos agregados por área y por mes: el registro individual
(dirección por cuadra, hora, marcas de violencia doméstica) nunca llega al lago.
La población por área sale del Censo (F07) con el mismo método que la de los distritos de consejo (_censo.py),
así que este script necesita CENSUS_API_KEY en .env.
"""
import datetime

from _censo import LICENCIA, nota_metodo, poblacion_por_area_lapd, por_10mil
from _comun import (URL_AREAS_LAPD, entre, escribir_lago, escribir_territorio, get_json, hoy, mes_anterior,
                    meses_completos, soql)

DATASET = "k7nn-b2ep"  # LAPD NIBRS Offenses Dataset
URL = f"https://data.lacity.org/resource/{DATASET}.json"
UNIDAD = "ofensas registradas (NIBRS)"
SIMPLE = "&maxAllowableOffset=0.003&geometryPrecision=4&f=geojson"  # unos 300 m, como los distritos de consejo

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
areas = soql(DATASET, select="area, area_name, count(*) AS n", where=W, group="area, area_name", order="n DESC")
mensual = soql(DATASET, select="date_trunc_ym(date_occ) AS mes, count(*) AS n",
               where=entre("date_occ", sini, fin), group="mes", order="mes")

# Las partes deben sumar el total: lo que no es Person/Property/Society (varias categorías a la vez) o viene vacío
# se declara aparte en vez de perderse
BASE = ("Person", "Property", "Society")
varias = sum(n for k, n in contra.items() if k is not None and k not in BASE)
sin_categoria = contra.get(None, 0)

# Límites de las 21 áreas (F18), simplificados para el mapa; la vigencia de los límites es la fecha de descarga
g = get_json(URL_AREAS_LAPD + SIMPLE)
feats = sorted(({"type": "Feature", "geometry": f["geometry"],
                 "properties": {"area": int(f["properties"]["PREC"]), "nombre": f["properties"]["APREC"].strip(),
                                "vigencia": hoy().isoformat()}} for f in g["features"]),
               key=lambda f: f["properties"]["area"])
assert [f["properties"]["area"] for f in feats] == list(range(1, 22)), "se esperaban las áreas 1 a 21"
assert sorted(int(r["area"]) for r in areas) == list(range(1, 22)), "los códigos de área de F01 no son 1 a 21"
escribir_territorio("areas_lapd", "F18",
                    "Geometría simplificada con maxAllowableOffset = 0,003 grados (unos 300 m) y 4 decimales: sirve "
                    "para mapas de la ciudad, no para medir ni para asignar hechos a un área. Vigencia = fecha de "
                    "descarga (la fuente no publica la suya).", feats)
pob = poblacion_por_area_lapd()

c = lambda v: {"valor": v, "unidad": UNIDAD, "vigencia": VIG, "fuente": "F01"}
escribir_lago(
    "seguridad",
    fuentes=[{"id": "F01", "nombre": "LAPD NIBRS Offenses Dataset", "url": URL,
              "estado": "vivo", "licencia": "no declara"},
             {"id": "F18", "nombre": "LAPD Divisions (LA GeoHub)", "url": URL_AREAS_LAPD.split("/query")[0],
              "estado": "vivo",
              "licencia": "This work is licensed under a Creative Commons Attribution 4.0 International License"},
             {"id": "F07", "nombre": "American Community Survey 5-Year Estimates (API)",
              "url": f"https://api.census.gov/data/{pob['anio']}/acs/acs5", "estado": "vivo", "licencia": LICENCIA}],
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
    tablas={"delitos_por_area": {
        "unidad": UNIDAD + "; habitantes (ACS); ofensas por 10.000 habitantes", "vigencia": VIG, "fuente": "F01",
        "columnas": ["area_nombre", "delitos_12m", "area", "poblacion", "delitos_por_10mil"],
        "filas": [[r["area_name"].strip(), int(r["n"]), int(r["area"]), pob["poblacion"][str(int(r["area"]))],
                   por_10mil(int(r["n"]), int(r["area"]), pob)] for r in areas],
        "poblacion_ciudad_acs": pob["poblacion_ciudad_acs"],
        "nota": f"Población por área de LAPD (F18, ACS {pob['anio']}, F07). "
                + nota_metodo(pob, "área", "F18")
                + " La tasa usa esa población: es una aproximación, no la población que LAPD atiende."}},
)
