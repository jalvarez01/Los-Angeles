"""Piezas del Censo de EE. UU. (fuente F07, ACS de 5 años). Solo biblioteca estándar, con llave en .env.

La llave nunca se imprime: los errores se limpian antes de mostrarse y la URL con llave no se guarda en el lago.
"""
import json
import urllib.error
import urllib.parse

from _comun import LAGO, URL_DISTRITOS, get_bytes, get_json, hoy, llave_census

BASE = "https://api.census.gov/data"
GAZETTEER = ("https://www2.census.gov/geo/docs/maps-data/data/gazetteer/"
             "{anio}_Gazetteer/{anio}_gaz_tracts_06.txt")
CACHE = LAGO / "raw" / "poblacion_distrito.json"


def api(anio, variables, para, en=None):
    """Una consulta a la API del ACS de 5 años. Devuelve la lista de filas sin la fila de títulos."""
    llave = llave_census()
    q = [("get", ",".join(variables)), ("for", para)] + [("in", e) for e in (en or [])] + [("key", llave)]
    try:
        filas = get_json(f"{BASE}/{anio}/acs/acs5?{urllib.parse.urlencode(q, safe=':,*')}")
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Census API {anio}: HTTP {e.code} (ver la llave en .env)") from None
    return filas[1:]


def lanzamientos():
    """Años del ACS de 5 años que responden con B13016, del más viejo al más nuevo."""
    años = []
    for a in range(2009, hoy().year + 1):
        try:
            api(a, ["B13016_001E"], "place:44000", ["state:06"])
            años.append(a)
        except SystemExit:
            continue
    return años


def _dentro(x, y, anillo):
    dentro = False
    j = len(anillo) - 1
    for i in range(len(anillo)):
        xi, yi = anillo[i][:2]
        xj, yj = anillo[j][:2]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            dentro = not dentro
        j = i
    return dentro


def _en_poligono(x, y, anillos):
    """Primer anillo = exterior, el resto = huecos."""
    return _dentro(x, y, anillos[0]) and not any(_dentro(x, y, h) for h in anillos[1:])


def distrito_de(x, y, distritos):
    for cd, partes in distritos:
        if any(_en_poligono(x, y, p) for p in partes):
            return cd
    return None


def poblacion_por_distrito():
    """Población (B01003_001E) de cada distrito de consejo, sumando los sectores censales del condado de
    Los Ángeles cuyo punto interno cae dentro del distrito. Se guarda en lago/raw (no va a git) para que
    todos los scripts usen la misma cifra dentro de una reconstrucción.
    """
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    anio = lanzamientos()[-1]
    sectores = {r[-1]: int(r[0]) for r in api(anio, ["B01003_001E"], "tract:*", ["state:06", "county:037"])}
    # Puntos internos de los sectores (Gazetteer del Censo, geografía de 2020: la del ACS desde 2020)
    filas = get_bytes(GAZETTEER.format(anio=2020)).decode("utf-8").splitlines()
    cab = [c.strip() for c in filas[0].split("\t")]
    puntos = {}
    for f in filas[1:]:
        v = f.split("\t")
        d = dict(zip(cab, v))
        if d["GEOID"].startswith("06037"):
            puntos[d["GEOID"][5:]] = (float(d["INTPTLONG"]), float(d["INTPTLAT"]))
    # Límites completos (sin simplificar) solo para asignar: no se guardan
    g = get_json(URL_DISTRITOS + "&f=geojson")
    distritos = []
    for f in g["features"]:
        geo = f["geometry"]
        partes = geo["coordinates"] if geo["type"] == "MultiPolygon" else [geo["coordinates"]]
        distritos.append((int(f["properties"]["District"]), partes))
    pob = {cd: 0 for cd, _ in distritos}
    n_sectores = {cd: 0 for cd, _ in distritos}
    fuera, sin_punto = 0, []
    for tr, hab in sectores.items():
        if tr not in puntos:
            sin_punto.append(tr)
            continue
        cd = distrito_de(*puntos[tr], distritos)
        if cd is None:
            fuera += hab
        else:
            pob[cd] += hab
            n_sectores[cd] += 1
    ciudad = int(api(anio, ["B01003_001E"], "place:44000", ["state:06"])[0][0])
    res = {"anio": anio, "poblacion": {str(k): v for k, v in sorted(pob.items())},
           "sectores": {str(k): v for k, v in sorted(n_sectores.items())},
           "poblacion_fuera": fuera, "sectores_sin_punto": len(sin_punto), "poblacion_ciudad_acs": ciudad}
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
    return res


def por_10mil(n, cd, pob):
    return round(10000 * n / pob["poblacion"][str(cd)], 1)
