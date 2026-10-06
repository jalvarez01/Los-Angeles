#!/usr/bin/env python3
"""Ingesta F10 · Equipamientos de la ciudad en OpenStreetMap (Overpass) -> lago/equipamientos.json

Se cuenta dentro del límite administrativo de la ciudad (relación OSM 207359), no por nombre.
Cobertura voluntaria: complementa los registros oficiales, no los sustituye.
"""
import urllib.parse

from _comun import escribir_lago, get_json

URL = "https://overpass-api.de/api/interpreter"
AREA = 3600207359  # relación 207359 «Los Angeles», admin_level 8 (la ciudad, no el condado)
CAPAS = {  # nombre en el lago: filtro OSM
    "hoteles": '["tourism"="hotel"]',
    "hospitales": '["amenity"="hospital"]',
    "colegios": '["amenity"="school"]',
    "parques": '["leisure"="park"]',
}

q = f"[out:json][timeout:60];area(id:{AREA})->.la;.la out tags;"
q += "".join(f"nwr{f}(area.la);out count;" for f in CAPAS.values())
r = get_json(URL, data=urllib.parse.urlencode({"data": q}).encode())

area, *conteos = r["elements"]
assert area["tags"].get("admin_level") == "8" and area["tags"].get("border_type") == "city", "el área no es la ciudad"
vig = r["osm3s"]["timestamp_osm_base"][:10]

escribir_lago(
    "equipamientos",
    fuentes=[{"id": "F10", "nombre": "OpenStreetMap vía Overpass API", "url": URL,
              "estado": "vivo", "licencia": "ODbL"}],
    cifras={k: {"valor": int(c["tags"]["total"]), "unidad": "elementos en OpenStreetMap",
                "vigencia": vig, "fuente": "F10"} for k, c in zip(CAPAS, conteos)},
)
