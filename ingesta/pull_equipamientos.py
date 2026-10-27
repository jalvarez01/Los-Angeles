#!/usr/bin/env python3
"""Ingesta F10 · Equipamientos de la ciudad en OpenStreetMap (Overpass) -> lago/equipamientos.json

Se cuenta dentro del límite administrativo de la ciudad (relación OSM 207359), no por nombre.
Cobertura voluntaria: complementa los registros oficiales, no los sustituye.
Colegios, hospitales y parques se asignan además a un distrito de consejo (F12) por punto en polígono al ingerir
(el centro que da Overpass para vías y relaciones); al lago solo llegan los conteos, nunca las coordenadas.
Las tasas usan la población por distrito del Censo (F07), así que este script necesita CENSUS_API_KEY en .env.
"""
import time
import urllib.error
import urllib.parse

from _censo import LICENCIA, distrito_de, poblacion_por_distrito, poligonos_distritos, por_10mil
from _comun import URL_DISTRITOS, escribir_lago, get_json

URL = "https://overpass-api.de/api/interpreter"
AREA = 3600207359  # relación 207359 «Los Angeles», admin_level 8 (la ciudad, no el condado)
CAPAS = {  # nombre en el lago: filtro OSM
    "hoteles": '["tourism"="hotel"]',
    "hospitales": '["amenity"="hospital"]',
    "colegios": '["amenity"="school"]',
    "parques": '["leisure"="park"]',
}
POR_DISTRITO = ("colegios", "hospitales", "parques")

q = f"[out:json][timeout:120];area(id:{AREA})->.la;.la out tags;"
q += "".join(f"nwr{f}(area.la);out count;" + ("out ids center qt;" if k in POR_DISTRITO else "")
             for k, f in CAPAS.items())
# Overpass responde 502/503/504 cuando está cargado: se reintenta con espera creciente
for intento in range(4):
    try:
        r = get_json(URL, data=urllib.parse.urlencode({"data": q}).encode())
        break
    except urllib.error.HTTPError as e:
        if e.code not in (429, 502, 503, 504) or intento == 3:
            raise
        print(f"Overpass HTTP {e.code}; reintento en {30 * (intento + 1)} s")
        time.sleep(30 * (intento + 1))

area, *resto = r["elements"]
assert area["tags"].get("admin_level") == "8" and area["tags"].get("border_type") == "city", "el área no es la ciudad"
vig = r["osm3s"]["timestamp_osm_base"][:10]

# Los elementos llegan en el orden de la consulta: cada «count» abre la capa siguiente
conteos, puntos, capas = {}, {k: [] for k in POR_DISTRITO}, iter(CAPAS)
for e in resto:
    if e["type"] == "count":
        actual = next(capas)
        conteos[actual] = int(e["tags"]["total"])
    else:
        c = e.get("center") or e
        puntos[actual].append((c["lon"], c["lat"]))
assert list(conteos) == list(CAPAS) and all(len(puntos[k]) == conteos[k] for k in POR_DISTRITO), \
    "la respuesta de Overpass no trae un punto por elemento"

zonas = poligonos_distritos()
pob = poblacion_por_distrito()
por_cd = {cd: {k: 0 for k in POR_DISTRITO} for cd in range(1, 16)}
sin_distrito = {k: 0 for k in POR_DISTRITO}
for k in POR_DISTRITO:
    for x, y in puntos[k]:
        cd = distrito_de(x, y, zonas)
        if cd is None:
            sin_distrito[k] += 1
        else:
            por_cd[cd][k] += 1
del puntos  # las coordenadas no salen de este script

escribir_lago(
    "equipamientos",
    fuentes=[{"id": "F10", "nombre": "OpenStreetMap vía Overpass API", "url": URL,
              "estado": "vivo", "licencia": "ODbL"},
             {"id": "F12", "nombre": "LA City Council Districts (Adopted 2021)", "url": URL_DISTRITOS.split("/query")[0],
              "estado": "vivo", "licencia": "no declara"},
             {"id": "F07", "nombre": "American Community Survey 5-Year Estimates (API)",
              "url": f"https://api.census.gov/data/{pob['anio']}/acs/acs5", "estado": "vivo", "licencia": LICENCIA}],
    cifras={k: {"valor": conteos[k], "unidad": "elementos en OpenStreetMap",
                "vigencia": vig, "fuente": "F10"} for k in CAPAS},
    tablas={"equipamientos_por_distrito": {
        "unidad": "elementos en OpenStreetMap; por 10.000 habitantes (ACS)", "vigencia": vig, "fuente": "F10",
        "columnas": ["cd", *POR_DISTRITO, *(f"{k}_por_10mil" for k in POR_DISTRITO)],
        "filas": [[cd, *(por_cd[cd][k] for k in POR_DISTRITO),
                   *(por_10mil(por_cd[cd][k], cd, pob, 2 if k == "hospitales" else 1) for k in POR_DISTRITO)] for cd in range(1, 16)],
        "sin_distrito": sin_distrito,
        "nota": "Cada elemento se asigna al distrito de consejo (límites completos de F12) que contiene su punto: el "
                "nodo, o el centro que calcula Overpass para vías y relaciones; un parque grande que cruza dos "
                "distritos cuenta solo en uno. "
                + ", ".join(f"{n} {k}" for k, n in sin_distrito.items())
                + " quedaron dentro de la ciudad pero fuera de los 15 polígonos (en el borde) y no se asignan. "
                f"Tasas con la población por distrito del ACS {pob['anio']} (F07); la de hospitales, con dos decimales "
                "porque hay pocos. No se guardan coordenadas."}},
)
