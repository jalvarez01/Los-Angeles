#!/usr/bin/env python3
"""Ingesta F09 · Metro Bike Share en tiempo real (GBFS) -> lago/movilidad.json

Es una foto del momento: la vigencia es la hora que el propio feed declara (last_updated),
no la hora en que corrió el script.
Las estaciones (station_information: nombre y coordenadas) son infraestructura pública, sin datos de personas;
se guardan con las bicis y anclajes de station_status para el mapa. La dirección de la estación no se guarda.
"""
import datetime

from _comun import escribir_lago, get_json

BASE = "https://gbfs.bcycle.com/bcycle_lametro"
URL = f"{BASE}/station_status.json"
URL_INFO = f"{BASE}/station_information.json"

st = get_json(URL)
s = st["data"]["stations"]
info = {x["station_id"]: x for x in get_json(URL_INFO)["data"]["stations"]}
vig = datetime.datetime.fromtimestamp(st["last_updated"], datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
estaciones = sorted([info[x["station_id"]]["name"].strip(), round(info[x["station_id"]]["lat"], 5),
                     round(info[x["station_id"]]["lon"], 5), x["num_bikes_available"], x["num_docks_available"]]
                    for x in s if x["station_id"] in info)
sin_info = len(s) - len(estaciones)

c = lambda v, u: {"valor": v, "unidad": u, "vigencia": vig, "fuente": "F09"}
escribir_lago(
    "movilidad",
    fuentes=[{"id": "F09", "nombre": "Metro Bike Share · GBFS station_status y station_information", "url": URL,
              "estado": "vivo", "licencia": "no declara"}],
    cifras={
        "estaciones": c(len(s), "estaciones"),
        "estaciones_operando": c(sum(1 for x in s if x.get("is_installed") and x.get("is_renting")), "estaciones"),
        "bicis_disponibles": c(sum(x["num_bikes_available"] for x in s), "bicicletas"),
        "anclajes_libres": c(sum(x["num_docks_available"] for x in s), "anclajes"),
        "bicis_electricas": c(sum((x.get("num_bikes_available_types") or {}).get("electric", 0) for x in s),
                              "bicicletas eléctricas"),
    },
    tablas={"estaciones": {
        "unidad": "grados WGS84; bicicletas disponibles; anclajes libres", "vigencia": vig, "fuente": "F09",
        "columnas": ["estacion", "lat", "lon", "bicis_disponibles", "anclajes_libres"], "filas": estaciones,
        "sin_coordenadas": sin_info,
        "nota": f"Nombre y coordenadas de {URL_INFO}; bicis y anclajes de station_status, en la misma foto. "
                f"{sin_info} estaciones de station_status no aparecen en station_information y no se mapean. "
                "Son estaciones (infraestructura pública), no viajes ni personas."}},
)
