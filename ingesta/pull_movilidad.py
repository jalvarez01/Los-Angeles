#!/usr/bin/env python3
"""Ingesta F09 · Metro Bike Share en tiempo real (GBFS) -> lago/movilidad.json

Es una foto del momento: la vigencia es la hora que el propio feed declara (last_updated),
no la hora en que corrió el script.
"""
import datetime

from _comun import escribir_lago, get_json

BASE = "https://gbfs.bcycle.com/bcycle_lametro"
URL = f"{BASE}/station_status.json"

st = get_json(URL)
s = st["data"]["stations"]
vig = datetime.datetime.fromtimestamp(st["last_updated"], datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")

c = lambda v, u: {"valor": v, "unidad": u, "vigencia": vig, "fuente": "F09"}
escribir_lago(
    "movilidad",
    fuentes=[{"id": "F09", "nombre": "Metro Bike Share · GBFS station_status", "url": URL,
              "estado": "vivo", "licencia": "no declara"}],
    cifras={
        "estaciones": c(len(s), "estaciones"),
        "estaciones_operando": c(sum(1 for x in s if x.get("is_installed") and x.get("is_renting")), "estaciones"),
        "bicis_disponibles": c(sum(x["num_bikes_available"] for x in s), "bicicletas"),
        "anclajes_libres": c(sum(x["num_docks_available"] for x in s), "anclajes"),
        "bicis_electricas": c(sum((x.get("num_bikes_available_types") or {}).get("electric", 0) for x in s),
                              "bicicletas eléctricas"),
    },
)
