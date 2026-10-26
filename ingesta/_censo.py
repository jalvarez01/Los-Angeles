"""Piezas del Censo de EE. UU. (fuente F07, ACS de 5 años). Solo biblioteca estándar, con llave en .env.

La llave nunca se imprime: los errores se limpian antes de mostrarse y la URL con llave no se guarda en el lago.
"""
import json
import urllib.error
import urllib.parse

from _comun import LAGO, URL_AREAS_LAPD, URL_DISTRITOS, get_bytes, get_json, hoy, llave_census

BASE = "https://api.census.gov/data"
GAZETTEER = ("https://www2.census.gov/geo/docs/maps-data/data/gazetteer/"
             "{anio}_Gazetteer/{anio}_gaz_tracts_06.txt")
CACHE = LAGO / "raw" / "poblacion_distrito.json"
CACHE_AREAS = LAGO / "raw" / "poblacion_area_lapd.json"
# Texto copiado de https://www.census.gov/data/developers/about/terms-of-service.html (consultado el día de la ingesta)
LICENCIA = ('Census Bureau API Terms of Service (census.gov/data/developers/about/terms-of-service.html): '
            '"You may use the Census Bureau API to develop a service or service to search, display, analyze, '
            'retrieve, view and otherwise \"get\" information from Census Bureau data." Atribución exigida: '
            '"This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau."')


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


def poligonos(url, clave):
    """Límites completos (sin simplificar) de una capa ArcGIS, solo para asignar: no se guardan.
    Devuelve [(clave(propiedades), partes)], con cada parte como lista de anillos."""
    g = get_json(url + "&f=geojson")
    assert not g.get("properties", {}).get("exceededTransferLimit"), f"respuesta truncada: {url}"
    res = []
    for f in g["features"]:
        geo = f["geometry"]
        partes = geo["coordinates"] if geo["type"] == "MultiPolygon" else [geo["coordinates"]]
        res.append((clave(f["properties"]), partes))
    return res


def poligonos_distritos():
    return poligonos(URL_DISTRITOS, lambda p: int(p["District"]))


def _puntos_sectores():
    """Puntos internos de los sectores del condado (Gazetteer del Censo, geografía de 2020: la del ACS desde 2020)."""
    filas = get_bytes(GAZETTEER.format(anio=2020)).decode("utf-8").splitlines()
    cab = [c.strip() for c in filas[0].split("\t")]
    puntos = {}
    for f in filas[1:]:
        d = dict(zip(cab, f.split("\t")))
        if d["GEOID"].startswith("06037"):
            puntos[d["GEOID"][5:]] = (float(d["INTPTLONG"]), float(d["INTPTLAT"]))
    return puntos


def suma_por_poligono(anio, variables, zonas):
    """Suma variables del ACS de los sectores censales del condado de Los Ángeles cuyo punto interno cae dentro de
    cada zona. Un sector que cruza un límite se asigna entero a la zona de su punto interno."""
    sectores = {r[-1]: [int(x) for x in r[:len(variables)]]
                for r in api(anio, variables, "tract:*", ["state:06", "county:037"])}
    assert all(x >= 0 for v in sectores.values() for x in v), "el Censo devolvió códigos de anotación negativos"
    puntos = _puntos_sectores()
    suma = {k: [0] * len(variables) for k, _ in zonas}
    n_sectores = {k: 0 for k, _ in zonas}
    fuera, sin_punto = [0] * len(variables), 0
    for tr, vals in sectores.items():
        if tr not in puntos:
            sin_punto += 1
            continue
        k = distrito_de(*puntos[tr], zonas)
        destino = fuera if k is None else suma[k]
        for i, x in enumerate(vals):
            destino[i] += x
        if k is not None:
            n_sectores[k] += 1
    return {"suma": suma, "sectores": n_sectores, "fuera": fuera, "sin_punto": sin_punto}


def _poblacion(cache, zonas):
    """Población (B01003_001E) por zona con suma_por_poligono. Se guarda en lago/raw (no va a git) para que
    todos los scripts usen la misma cifra dentro de una reconstrucción."""
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    anio = lanzamientos()[-1]
    r = suma_por_poligono(anio, ["B01003_001E"], zonas)
    ciudad = int(api(anio, ["B01003_001E"], "place:44000", ["state:06"])[0][0])
    res = {"anio": anio, "poblacion": {str(k): v[0] for k, v in sorted(r["suma"].items())},
           "sectores": {str(k): v for k, v in sorted(r["sectores"].items())},
           "poblacion_fuera": r["fuera"][0], "sectores_sin_punto": r["sin_punto"], "poblacion_ciudad_acs": ciudad}
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
    return res


def poblacion_por_distrito():
    """Población de cada distrito de consejo (límites completos de F12)."""
    return _poblacion(CACHE, poligonos_distritos())


def poblacion_por_area_lapd():
    """Población de cada una de las 21 áreas de LAPD (límites completos de F18)."""
    return _poblacion(CACHE_AREAS, poligonos(URL_AREAS_LAPD, lambda p: int(p["PREC"])))


def por_10mil(n, cd, pob, decimales=1):
    return round(10000 * n / pob["poblacion"][str(cd)], decimales)


def nota_metodo(pob, zonas, capa):
    """Nota de método y error para una tabla de población por zona, como la de poblacion_por_distrito."""
    miles = lambda n: f"{n:,}".replace(",", ".")
    total = sum(pob["poblacion"].values())
    dif = total - pob["poblacion_ciudad_acs"]
    return (f"Método: se suman los {miles(sum(pob['sectores'].values()))} sectores censales del condado de Los Ángeles "
            f"(ACS {pob['anio']}, B01003_001E) cuyo punto interno (Gazetteer del Censo 2020) cae dentro de cada "
            f"{zonas}, usando los límites completos de {capa} (sin simplificar). Error: un sector que cruza el límite de "
            f"dos zonas se asigna entero a la zona de su punto interno, así que cada {zonas} puede quedar algo por encima "
            f"o por debajo; ese error no se puede medir con esta fuente. A escala de ciudad, la suma ({miles(total)}) "
            f"difiere {'+' if dif >= 0 else '-'}{miles(abs(dif))} habitantes "
            f"({100 * dif / pob['poblacion_ciudad_acs']:+.2f} %) de la población de la ciudad en el mismo ACS "
            f"({miles(pob['poblacion_ciudad_acs'])}). Son estimaciones de encuesta con margen de error, no un censo.")
