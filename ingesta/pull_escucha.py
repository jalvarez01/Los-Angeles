#!/usr/bin/env python3
"""Ingesta F11 · Cuánta gente busca la ciudad en Wikipedia -> lago/escucha.json

Es el script base del taller, tal cual, con CIUDAD = «Los Ángeles».
"""
import datetime
import urllib.parse

from _comun import escribir_lago, get_json, meses_completos

CIUDAD = "Los Ángeles"  # título del artículo en es.wikipedia
ini, fin = meses_completos(20)  # meses completos
hasta = (fin - datetime.timedelta(days=1)).strftime("%Y%m%d")

# Un título que coincide no es la cosa: se exige artículo y se usa el título canónico
t = urllib.parse.quote(CIUDAD.replace(" ", "_"))
resumen = get_json(f"https://es.wikipedia.org/api/rest_v1/page/summary/{t}")
assert resumen["type"] == "standard", f"«{CIUDAD}» no es un artículo sino {resumen['type']}"
canon = urllib.parse.quote(resumen["titles"]["canonical"])

url =("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
       f"es.wikipedia/all-access/user/{canon}/monthly/{ini:%Y%m%d}/{hasta}")
puntos = [[i["timestamp"][:4] + "-" + i["timestamp"][4:6], i["views"]] for i in get_json(url)["items"]]
ultimo = puntos[-1]

escribir_lago(
    "escucha",
    fuentes=[{"id": "F11", "nombre": "Wikimedia Pageviews API", "url": url, "estado": "vivo", "licencia": "CC0"}],
    cifras={"vistas_ultimo_mes": {"valor": ultimo[1], "unidad": "vistas de personas",
                                  "vigencia": ultimo[0], "fuente": "F11"}},
    series={"vistas_mensuales": {"unidad": "vistas de personas", "fuente": "F11", "puntos": puntos}},
)
