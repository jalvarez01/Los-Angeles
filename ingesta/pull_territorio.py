#!/usr/bin/env python3
"""Ingesta F12 · Límites de los 15 distritos de consejo (LA GeoHub) -> territorio/distritos_consejo.geojson

GeoJSON en WGS84, simplificado (maxAllowableOffset = 0,003 grados, unos 300 m, y 4 decimales) para que la capa
pese poco. La capa completa (sin simplificar) también es pública y no pide llave; pesa unos 1,3 MB.
La vigencia de los nombres de los concejales es la fecha de descarga: la fuente no publica la suya.
"""
import json

from _comun import RAIZ, TERRITORIO, URL_DISTRITOS, get_json, hoy

URL = URL_DISTRITOS + "&maxAllowableOffset=0.003&geometryPrecision=4&f=geojson"

g = get_json(URL)
feats = []
for f in g["features"]:
    feats.append({"type": "Feature", "geometry": f["geometry"],
                  "properties": {"cd": int(f["properties"]["District"]), "nombre": f["properties"]["NAME"],
                                 "vigencia": hoy().isoformat()}})
feats.sort(key=lambda f: f["properties"]["cd"])
assert [f["properties"]["cd"] for f in feats] == list(range(1, 16)), "se esperaban los distritos 1 a 15"

TERRITORIO.mkdir(exist_ok=True)
ruta = TERRITORIO / "distritos_consejo.geojson"
ruta.write_text(json.dumps({"type": "FeatureCollection", "fuente": "F12",
                           "nota": "Geometría simplificada con maxAllowableOffset = 0,003 grados (unos 300 m) y 4 "
                                   "decimales: sirve para mapas de la ciudad, no para medir ni para asignar "
                                   "predios a un distrito. Vigencia de los nombres = fecha de descarga.",
                           "features": feats}, ensure_ascii=False,
                           separators=(",", ":")) + "\n", encoding="utf-8")
print(f"escrito {ruta.relative_to(RAIZ)}")
