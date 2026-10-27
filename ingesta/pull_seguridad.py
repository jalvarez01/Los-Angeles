#!/usr/bin/env python3
"""Ingesta F01 · Ofensas registradas por LAPD (NIBRS) -> lago/seguridad.json
y F18 · Áreas de LAPD, F19 · Distritos de reporte de LAPD (LA GeoHub) -> territorio/

Solo se bajan conteos agregados por área, distrito de reporte y mes: el registro individual
(dirección por cuadra, hora, marcas de violencia doméstica) nunca llega al lago.
Por distrito de reporte, las celdas con menos de 10 ofensas se suprimen (ver suprimir()).
La población por área sale del Censo (F07) con el mismo método que la de los distritos de consejo (_censo.py),
así que este script necesita CENSUS_API_KEY en .env.
"""
import datetime

from _censo import LICENCIA, nota_metodo, poblacion_por_area_lapd, por_10mil
from _comun import (URL_AREAS_LAPD, URL_RD_LAPD, entre, escribir_lago, escribir_territorio, get_json, hoy,
                    mes_anterior, meses_completos, soql)

DATASET = "k7nn-b2ep"  # LAPD NIBRS Offenses Dataset
URL = f"https://data.lacity.org/resource/{DATASET}.json"
UNIDAD = "ofensas registradas (NIBRS)"
SIMPLE = "&maxAllowableOffset=0.003&geometryPrecision=4&f=geojson"  # unos 300 m, como los distritos de consejo
SIMPLE_RD = "&maxAllowableOffset=0.0005&geometryPrecision=4&f=geojson"  # unos 50 m: los distritos son pequeños
UMBRAL = 10


def suprimir(filas):
    """filas: [rd, area, n, en_capa]. Devuelve [rd, area, n o None, suprimido, en_capa].

    Toda celda con 1 a 9 ofensas se guarda como None. Si en un área queda una sola celda suprimida, se suprime
    también la celda visible más pequeña de esa área (supresión complementaria): el total por área es público
    y, con una sola celda oculta, bastaría restar para despejarla. Las celdas con 0 se publican.
    """
    ocultas = {i for i, f in enumerate(filas) if 0 < f[2] < UMBRAL}
    for area in {f[1] for f in filas}:
        idx = [i for i, f in enumerate(filas) if f[1] == area]
        if len([i for i in idx if i in ocultas]) == 1:
            visibles = [i for i in idx if i not in ocultas and filas[i][2] > 0]
            if visibles:
                ocultas.add(min(visibles, key=lambda i: filas[i][2]))
    return [[rd, area, None if i in ocultas else n, i in ocultas, en_capa]
            for i, (rd, area, n, en_capa) in enumerate(filas)]

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

# Distritos de reporte (F19): conteo en el servidor por área y distrito, en la misma ventana
g = get_json(URL_RD_LAPD + SIMPLE_RD)
assert not g.get("properties", {}).get("exceededTransferLimit"), "capa de distritos de reporte truncada"
rd_geo = {f"{f['properties']['REPDIST']:04d}": int(f["properties"]["PREC"]) for f in g["features"]}
assert len(rd_geo) == len(g["features"]) > 1000, "códigos de distrito de reporte repetidos o capa incompleta"
escribir_territorio("distritos_reporte_lapd", "F19",
                    "Geometría simplificada con maxAllowableOffset = 0,0005 grados (unos 50 m) y 4 decimales; cada "
                    "polígono se simplifica por separado, así que puede haber huecos o traslapes pequeños entre "
                    "vecinos. Sirve para mapas, no para medir. Vigencia = fecha de descarga.",
                    sorted(({"type": "Feature", "geometry": f["geometry"],
                             "properties": {"rd": f"{f['properties']['REPDIST']:04d}",
                                            "area": int(f["properties"]["PREC"]), "vigencia": hoy().isoformat()}}
                            for f in g["features"]), key=lambda f: f["properties"]["rd"]))
nibrs = {r["rpt_dist_no"].zfill(4): (int(r["area"]), int(r["n"])) for r in
         soql(DATASET, select="area, rpt_dist_no, count(*) AS n", where=W, group="area, rpt_dist_no", limit=50000)}
rd_filas = suprimir(sorted([[rd, rd_geo.get(rd, a), n, rd in rd_geo] for rd, (a, n) in nibrs.items()]
                           + [[rd, a, 0, True] for rd, a in rd_geo.items() if rd not in nibrs]))
n_supr = sum(1 for f in rd_filas if f[3])
n_peq = sum(1 for _, (_, n) in nibrs.items() if 0 < n < UMBRAL)  # solo el total: no se dice cuáles son
sin_capa = [f for f in rd_filas if not f[4]]

c = lambda v: {"valor": v, "unidad": UNIDAD, "vigencia": VIG, "fuente": "F01"}
escribir_lago(
    "seguridad",
    fuentes=[{"id": "F01", "nombre": "LAPD NIBRS Offenses Dataset", "url": URL,
              "estado": "vivo", "licencia": "no declara"},
             {"id": "F18", "nombre": "LAPD Divisions (LA GeoHub)", "url": URL_AREAS_LAPD.split("/query")[0],
              "estado": "vivo",
              "licencia": "This work is licensed under a Creative Commons Attribution 4.0 International License"},
             {"id": "F19", "nombre": "LAPD Reporting District (LA GeoHub)", "url": URL_RD_LAPD.split("/query")[0],
              "estado": "vivo", "licencia": "no declara"},
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
                + " La tasa usa esa población: es una aproximación, no la población que LAPD atiende."},
        "delitos_por_distrito_reporte": {
            "unidad": UNIDAD, "vigencia": VIG, "fuente": "F01",
            "columnas": ["rd", "area", "delitos_12m", "suprimido", "en_capa"], "filas": rd_filas,
            "nota": f"Regla de supresión: toda celda con menos de {UMBRAL} ofensas (de 1 a 9) se guarda como null con "
                    "suprimido = true, nunca el número. Si en un área queda una sola celda suprimida, se suprime "
                    "también la celda visible más pequeña de esa área, para que no se pueda despejar restando del total "
                    f"del área. {n_supr} celdas suprimidas: {n_peq} con 1 a 9 ofensas y {n_supr - n_peq} complementarias. Las celdas con 0 son distritos de F19 sin ofensas en la "
                    f"ventana. {len(sin_capa)} códigos de F01 no tienen polígono en F19 (en_capa = false; códigos "
                    f"{', '.join(f[0] for f in sin_capa)}). El área de cada distrito es la de F19; para los que no "
                    "tienen polígono, la de F01."}},
)
