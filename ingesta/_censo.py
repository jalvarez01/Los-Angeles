"""Piezas del Censo de EE. UU. (fuente F07, ACS de 5 años). Solo biblioteca estándar, con llave en .env.

La llave nunca se imprime: los errores se limpian antes de mostrarse y la URL con llave no se guarda en el lago.
"""
import json
import math
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
Z90 = 1.645  # los MOE del ACS se publican al 90 % de confianza
CONTROLADO = -555555555  # anotación del Censo: estimación controlada, el MOE no aplica y se toma como 0
NOTA_MOE = ("Margen de error (MOE, 90 % de confianza, como lo publica el Census Bureau): el de la población de cada "
            "zona es la raíz de la suma de los MOE² de sus sectores censales, la aproximación que el Census Bureau da "
            "para estimaciones derivadas; puede quedar conservadora u optimista según cuánto se correlacionen los "
            "sectores. Una tasa con numerador exacto (conteo administrativo) y denominador del ACS hereda MOE_tasa = "
            "tasa × MOE_pob / pob; ese MOE solo mide la incertidumbre del denominador del ACS, porque el conteo se toma "
            "como exacto (no modela la variación aleatoria de un año a otro). Se guarda con un decimal más que la tasa. "
            "La columna _dif_significativa aplica la prueba del Census Bureau contra la ciudad: "
            "|tasa_zona − tasa_ciudad| / raíz(EE_zona² + EE_ciudad²) > 1,645, con EE = MOE / 1,645; la ciudad es la "
            "suma de las zonas de la tabla (referencia_ciudad), que incluye a cada zona, así que la prueba es "
            "aproximada. Si dos zonas se traslapan en su intervalo ± MOE, la diferencia entre ellas no es significativa.")


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
    es_moe = [v.endswith("M") for v in variables]
    sectores = {r[-1]: [valor(v, x) for v, x in zip(variables, r)]
                for r in api(anio, variables, "tract:*", ["state:06", "county:037"])}
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
            destino[i] += x ** 2 if es_moe[i] else x  # los MOE se suman en cuadratura
        if k is not None:
            n_sectores[k] += 1
    raiz = lambda v: [math.sqrt(x) if m else x for x, m in zip(v, es_moe)]
    return {"suma": {k: raiz(v) for k, v in suma.items()}, "sectores": n_sectores, "fuera": raiz(fuera),
            "sin_punto": sin_punto}


def valor(variable, x):
    """Valor numérico de una celda del ACS. Un MOE con la anotación de estimación controlada vale 0; cualquier otro
    código de anotación negativo detiene la ingesta en vez de colarse como número."""
    x = int(float(x))
    if variable.endswith("M") and x == CONTROLADO:
        return 0
    if x < 0:
        raise SystemExit(f"{variable}: el Censo devolvió el código de anotación {x}")
    return x


def _poblacion(cache, zonas):
    """Población (B01003_001E) por zona con suma_por_poligono. Se guarda en lago/raw (no va a git) para que
    todos los scripts usen la misma cifra dentro de una reconstrucción."""
    if cache.exists():
        res = json.loads(cache.read_text(encoding="utf-8"))
        if "poblacion_moe" in res:  # una caché vieja, sin MOE, se recalcula
            return res
    anio = lanzamientos()[-1]
    var = ["B01003_001E", "B01003_001M"]
    r = suma_por_poligono(anio, var, zonas)
    est, moe = (valor(v, x) for v, x in zip(var, api(anio, var, "place:44000", ["state:06"])[0]))
    res = {"anio": anio, "poblacion": {str(k): v[0] for k, v in sorted(r["suma"].items())},
           "poblacion_moe": {str(k): round(v[1]) for k, v in sorted(r["suma"].items())},
           "sectores": {str(k): v for k, v in sorted(r["sectores"].items())},
           "poblacion_fuera": r["fuera"][0], "sectores_sin_punto": r["sin_punto"],
           "poblacion_ciudad_acs": est, "poblacion_ciudad_acs_moe": moe}
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


def moe_tasa(tasa, pob, moe_pob):
    """MOE de una tasa con numerador exacto y denominador estimado por el ACS: tasa × MOE_pob / pob."""
    return abs(tasa) * moe_pob / pob


def moe_proporcion(x, y, mx, my):
    """MOE de p = y / x (fórmula de proporción del Census Bureau). Si el radicando queda negativo, se usa la de razón,
    con + en lugar de −. Devuelve (MOE de p, fórmula usada)."""
    p = y / x
    rad = my ** 2 - p ** 2 * mx ** 2
    if rad < 0:
        return math.sqrt(my ** 2 + p ** 2 * mx ** 2) / x, "razón"
    return math.sqrt(rad) / x, "proporción"


def significativa(r, m, rc, mc):
    """Prueba del Census Bureau a 90 %: |r − rc| / raíz(EE² + EE_c²) > 1,645, con EE = MOE / 1,645."""
    se = math.hypot(m / Z90, mc / Z90)
    return abs(r - rc) > 0 if se == 0 else abs(r - rc) / se > Z90


def con_moe(columnas, filas, pob, zona="cd", bases=None, decimales=None):
    """Agrega al final de la tabla, por cada columna de tasa <x>_por_10mil, <x>_por_10mil_moe y
    <x>_por_10mil_dif_significativa (contra la ciudad = suma de las zonas de la tabla). El MOE lleva un decimal más
    que la tasa, para que no se redondee a 0 cuando es pequeño. La prueba se hace con los
    valores ya redondeados que se guardan, para que el verificador la pueda repetir igual.
    Devuelve (columnas, filas, referencia_ciudad)."""
    bases, decimales = bases or {}, decimales or {}
    iz = columnas.index(zona)
    zonas = [str(f[iz]) for f in filas]
    pob_ref = sum(pob["poblacion"][z] for z in zonas)
    moe_ref = math.sqrt(sum(pob["poblacion_moe"][z] ** 2 for z in zonas))
    ref = {"poblacion": pob_ref, "poblacion_moe": round(moe_ref)}
    nuevas, extra = [], [[] for _ in filas]
    for t in [c for c in columnas if c.endswith("_por_10mil")]:
        d = decimales.get(t, 1)
        ib, it = columnas.index(bases.get(t, t[:-len("_por_10mil")])), columnas.index(t)
        rc_u = 10000 * sum(f[ib] for f in filas) / pob_ref
        rc, mc = round(rc_u, d), round(moe_tasa(rc_u, pob_ref, moe_ref), d + 1)
        ref[t] = [rc, mc]
        for f, e, z in zip(filas, extra, zonas):
            m = round(moe_tasa(10000 * f[ib] / pob["poblacion"][z], pob["poblacion"][z], pob["poblacion_moe"][z]), d + 1)
            e += [m, significativa(f[it], m, rc, mc)]
        nuevas += [t + "_moe", t + "_dif_significativa"]
    return columnas + nuevas, [f + e for f, e in zip(filas, extra)], ref


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
