"""Piezas comunes de la ingesta. Solo biblioteca estándar de Python, sin llaves."""
import datetime
import json
import pathlib
import urllib.parse
import urllib.request

UA = {"User-Agent": "taller-sistemas-de-informacion/1.0 (curso universitario EAFIT)"}
RAIZ = pathlib.Path(__file__).resolve().parent.parent
URL_DISTRITOS = ("https://maps.lacity.org/lahub/rest/services/Boundaries/MapServer/13/query"
                 "?where=1%3D1&outFields=District,NAME&returnGeometry=true&outSR=4326")
LAGO = RAIZ / "lago"
TERRITORIO = RAIZ / "territorio"


def hoy():
    return datetime.date.today()


def get_bytes(url, data=None, timeout=120):
    req = urllib.request.Request(url, data=data, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def get_json(url, data=None):
    return json.loads(get_bytes(url, data))


def soql(dataset, **params):
    """Consulta SODA a data.lacity.org: el servidor filtra y agrega, y solo baja el resultado."""
    q = urllib.parse.urlencode({"$" + k: v for k, v in params.items()})
    return get_json(f"https://data.lacity.org/resource/{dataset}.json?{q}")


def meses_completos(n, ref=None):
    """Los últimos n meses completos: (primer día del primero, primer día del mes en curso)."""
    fin = (ref or hoy()).replace(day=1)
    y, m = fin.year, fin.month - n
    while m <= 0:
        m += 12
        y -= 1
    return datetime.date(y, m, 1), fin


def mes_anterior(d):
    return (d - datetime.timedelta(days=1)).strftime("%Y-%m")


def entre(campo, ini, fin):
    return f"{campo} >= '{ini}T00:00:00' AND {campo} < '{fin}T00:00:00'"


def llave_census():
    """Lee CENSUS_API_KEY de .env en la raíz (o del entorno). Nunca se imprime ni se guarda en el lago."""
    import os
    env = RAIZ / ".env"
    if env.exists():
        for linea in env.read_text(encoding="utf-8").splitlines():
            k, _, v = linea.partition("=")
            if k.strip() == "CENSUS_API_KEY" and v.strip():
                return v.strip().strip("'\"")
    if os.environ.get("CENSUS_API_KEY"):
        return os.environ["CENSUS_API_KEY"]
    raise SystemExit("Falta CENSUS_API_KEY: ponla en .env (llave gratuita en api.census.gov/data/key_signup.html)")


def escribir_lago(tema, fuentes, cifras, series=None, tablas=None, fusionar=False):
    """Escribe lago/<tema>.json con la forma del contrato: toda cifra con valor, unidad, vigencia y fuente.

    Con fusionar=True conserva lo que ya hubiera en el archivo (otra fuente del mismo tema) y solo
    reemplaza lo que este script trae; así dos scripts pueden alimentar un mismo tema sin pisarse.
    """
    LAGO.mkdir(exist_ok=True)
    ruta = LAGO / f"{tema}.json"
    if fusionar and ruta.exists():
        previo = json.loads(ruta.read_text(encoding="utf-8"))
        ids = {f["id"] for f in fuentes}
        fuentes = [f for f in previo.get("fuentes", []) if f["id"] not in ids] + fuentes
        cifras = {**previo.get("cifras", {}), **cifras}
        series = {**previo.get("series", {}), **(series or {})}
        tablas = {**previo.get("tablas", {}), **(tablas or {})}
    lago = {"tema": tema, "probado": hoy().isoformat(), "fuentes": fuentes, "cifras": cifras}
    if series:
        lago["series"] = series
    if tablas:
        lago["tablas"] = tablas
    ruta.write_text(json.dumps(lago, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"escrito {ruta.relative_to(RAIZ)}")
    return lago
