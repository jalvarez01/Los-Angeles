#!/usr/bin/env python3
"""Verificación antes de publicar: con un solo FAIL no se despliega.

Adaptada del verificador del taller: el contrato (con nuestra extensión «tablas»),
datos personales con formato de EE. UU. y comprobaciones de dominio para Los Ángeles.
"""
import datetime
import glob
import json
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
fallos = 0
PII = re.compile(r"[\w.+-]+@[\w-]+\.[a-z]{2,}"                 # correos
                 r"|\(?\b\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b"     # teléfonos de EE. UU.
                 r"|\b\d{3}-\d{2}-\d{4}\b")                    # números de seguro social
CAMPOS_PERSONALES = re.compile(r"telefono|phone|correo|email|ssn|vict|apn|address|direccion|"
                               r"first_name|last_name|contractor|applicant", re.I)
MES = re.compile(r"\d{4}-\d{2}")


def check(nombre, ok, detalle=""):
    global fallos
    print(("PASS " if ok else "FAIL ") + nombre + ("" if ok else f"  <- {detalle}"))
    fallos += 0 if ok else 1


def recorre(x, clave=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield k, None
            yield from recorre(v, k)
    elif isinstance(x, list):
        for v in x:
            yield from recorre(v, clave)
    else:
        yield clave, x


lagos = {}
for ruta in sorted(glob.glob(str(RAIZ / "lago" / "*.json"))):
    nombre = "lago/" + pathlib.Path(ruta).name
    lago = json.load(open(ruta, encoding="utf-8"))
    lagos[lago.get("tema")] = lago
    fuentes = lago.get("fuentes", [])
    ids = {f.get("id") for f in fuentes}
    check(f"{nombre}: probado es un día", re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(lago.get("probado"))),
          lago.get("probado"))
    check(f"{nombre}: toda fuente con id, url y licencia",
          fuentes and all(f.get("id") and f.get("url") and f.get("licencia") for f in fuentes))
    for clave, c in lago.get("cifras", {}).items():
        completa = c.get("valor") is not None and c.get("unidad") and c.get("vigencia") and c.get("fuente") in ids
        check(f"{nombre}: {clave} con valor, unidad, vigencia y fuente conocida", completa, c)
    for clave, s in lago.get("series", {}).items():
        meses = [p[0] for p in s.get("puntos", [])]
        ok = s.get("unidad") and s.get("fuente") in ids and meses and all(MES.fullmatch(m) for m in meses)
        check(f"{nombre}: serie {clave} con unidad, fuente y meses AAAA-MM", ok, s.get("fuente"))
        check(f"{nombre}: serie {clave} ordenada y sin meses repetidos", meses == sorted(set(meses)))
    for clave, t in lago.get("tablas", {}).items():
        cols = t.get("columnas", [])
        ok = t.get("unidad") and t.get("vigencia") and t.get("fuente") in ids and t.get("filas")
        check(f"{nombre}: tabla {clave} con unidad, vigencia y fuente conocida", ok)
        check(f"{nombre}: tabla {clave} con filas del ancho de sus columnas",
              all(len(f) == len(cols) for f in t.get("filas", [])))
    pares = list(recorre(lago))
    sospechosos = sorted({k for k, _ in pares if CAMPOS_PERSONALES.search(k)}
                         | {c for t in lago.get("tablas", {}).values() for c in t.get("columnas", [])
                            if CAMPOS_PERSONALES.search(c)})
    check(f"{nombre}: ningún campo con nombre de dato personal", not sospechosos, sospechosos)
    hallado = next((v for _, v in pares if isinstance(v, str) and PII.search(v)), None)
    check(f"{nombre}: ningún texto con correo, teléfono o SSN", hallado is None, hallado)

# Comprobaciones de dominio para Los Ángeles
v = lambda tema, clave: lagos[tema]["cifras"][clave]["valor"]
filas = lambda tema, clave: lagos[tema]["tablas"][clave]["filas"]
if "demografia" in lagos:
    pob = v("demografia", "poblacion")
    check("población de la ciudad (no del condado) en un rango sensato", 3_000_000 < pob < 4_500_000, pob)
    check("viviendas menos que habitantes", 0 < v("demografia", "viviendas") < pob)
if "seguridad" in lagos:
    ta = lagos["seguridad"]["tablas"]["delitos_por_area"]
    areas = ta["filas"]
    ia = {c: ta["columnas"].index(c) for c in ta["columnas"]}
    check("LAPD tiene 21 áreas", len(areas) == 21, len(areas))
    check("las áreas suman el total de delitos", sum(f[ia["delitos_12m"]] for f in areas) == v("seguridad", "delitos_12m"))
    partes = ("personas", "propiedad", "sociedad", "varias_categorias", "sin_categoria")
    check("personas + propiedad + sociedad + varias + sin categoría = total exacto",
          sum(v("seguridad", f"delitos_{'contra_' if p in partes[:3] else ''}{p}_12m") for p in partes)
          == v("seguridad", "delitos_12m"))
    check("personas + propiedad no superan el total",
          v("seguridad", "delitos_contra_personas_12m") + v("seguridad", "delitos_contra_propiedad_12m")
          <= v("seguridad", "delitos_12m"))
    check("áreas · códigos 1 a 21 sin repetir", sorted(f[ia["area"]] for f in areas) == list(range(1, 22)))
    pa = sum(f[ia["poblacion"]] for f in areas)
    check("áreas · población suma cerca de la de la ciudad en el mismo ACS (±1 %)",
          abs(pa - ta["poblacion_ciudad_acs"]) / ta["poblacion_ciudad_acs"] < 0.01, (pa, ta["poblacion_ciudad_acs"]))
    check("áreas · ofensas por 10.000 habitantes recalculadas",
          all(abs(f[ia["delitos_por_10mil"]] - 10000 * f[ia["delitos_12m"]] / f[ia["poblacion"]]) < 0.06 for f in areas))
    check("áreas · la nota dice el método y el error", "Método" in ta.get("nota", "") and "Error" in ta["nota"])
    areas_geo = RAIZ / "territorio" / "areas_lapd.geojson"
    check("áreas · existe territorio/areas_lapd.geojson", areas_geo.exists())
    if areas_geo.exists():
        g = json.load(open(areas_geo, encoding="utf-8"))
        check("áreas · los códigos del lago coinciden con los de la geometría",
              sorted(f["properties"]["area"] for f in g["features"]) == sorted(f[ia["area"]] for f in areas))
        check("áreas · geometría con fuente, nota de simplificación y vigencia (F18)",
              g.get("fuente") == "F18" and "simplificada" in g.get("nota", "")
              and all(f["geometry"]["type"] in ("Polygon", "MultiPolygon")
                      and re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(f["properties"].get("vigencia")))
                      for f in g["features"]))
    tr = lagos["seguridad"]["tablas"].get("delitos_por_distrito_reporte")
    check("distritos de reporte · tabla presente", tr is not None)
    if tr:
        ir = {c: tr["columnas"].index(c) for c in tr["columnas"]}
        rf = tr["filas"]
        n = [f[ir["delitos_12m"]] for f in rf]
        check("distritos de reporte · ningún conteo guardado entre 1 y 9", not [x for x in n if x is not None and 0 < x < 10],
              [x for x in n if x is not None and 0 < x < 10][:5])
        check("distritos de reporte · null si y solo si suprimido",
              all((f[ir["delitos_12m"]] is None) == (f[ir["suprimido"]] is True) for f in rf))
        check("distritos de reporte · la nota dice la regla de supresión",
              "menos de 10" in tr.get("nota", "") and "suprim" in tr["nota"])
        check("distritos de reporte · sin códigos repetidos", len({f[ir["rd"]] for f in rf}) == len(rf))
        tot_area = {f[ia["area"]]: f[ia["delitos_12m"]] for f in areas}
        ok_comp, ok_suma = True, True
        for a, t in tot_area.items():
            fa = [f for f in rf if f[ir["area"]] == a]
            ocultas = sum(1 for f in fa if f[ir["suprimido"]])
            vis = sum(f[ir["delitos_12m"]] or 0 for f in fa)
            ok_comp &= ocultas != 1
            ok_suma &= vis == t if ocultas == 0 else vis < t
        check("distritos de reporte · ninguna área con una sola celda suprimida (supresión complementaria)", ok_comp)
        check("distritos de reporte · por área, visibles = total si no hay supresión y menor si la hay", ok_suma)
        check("distritos de reporte · visibles no superan el total de la ciudad",
              sum(x or 0 for x in n) <= v("seguridad", "delitos_12m"))
        rd_geo = RAIZ / "territorio" / "distritos_reporte_lapd.geojson"
        check("distritos de reporte · existe territorio/distritos_reporte_lapd.geojson", rd_geo.exists())
        if rd_geo.exists():
            g = json.load(open(rd_geo, encoding="utf-8"))
            geo = {f["properties"]["rd"]: f["properties"]["area"] for f in g["features"]}
            check("distritos de reporte · geometría con fuente, nota de simplificación y vigencia (F19)",
                  g.get("fuente") == "F19" and "simplificada" in g.get("nota", "") and len(geo) == len(g["features"])
                  and all(re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(f["properties"].get("vigencia"))) for f in g["features"]))
            check("distritos de reporte · en_capa coincide con la geometría",
                  all(f[ir["en_capa"]] == (f[ir["rd"]] in geo) for f in rf))
            check("distritos de reporte · todo polígono tiene fila", set(geo) <= {f[ir["rd"]] for f in rf})
            check("distritos de reporte · el área de cada distrito es la de su polígono y la del código",
                  all(geo[f[ir["rd"]]] == f[ir["area"]] == int(f[ir["rd"]]) // 100 for f in rf if f[ir["en_capa"]]))
            check("distritos de reporte · las áreas de la geometría son las 21 de F18",
                  sorted(set(geo.values())) == list(range(1, 22)))
if "municipio" in lagos:
    cds = filas("municipio", "solicitudes_por_distrito")
    check("311 · distritos 1 a 15", sorted(f[0] for f in cds) == list(range(1, 16)), [f[0] for f in cds])
    check("311 · los distritos no superan el total", sum(f[1] for f in cds) <= v("municipio", "solicitudes_anio"))
    check("311 · porcentaje entre 0 y 100", 0 <= v("municipio", "pct_cerradas") <= 100)
    check("311 · % cerradas sin informativas entre 0 y 100 y no mayor que el original",
          0 <= v("municipio", "pct_cerradas_sin_informativas") <= v("municipio", "pct_cerradas") <= 100)
    nota = lagos["municipio"]["tablas"]["solicitudes_por_distrito"].get("nota", "")
    sin = re.match(r"(\d+) solicitudes", nota)
    check("311 · distritos + sin distrito = total exacto",
          sin and sum(f[1] for f in cds) + int(sin.group(1)) == v("municipio", "solicitudes_anio"), nota)
if "vivienda" in lagos:
    cds = filas("vivienda", "permisos_por_distrito")
    check("permisos · distritos 1 a 15", sorted(f[0] for f in cds) == list(range(1, 16)))
    check("permisos · los distritos no superan el total", sum(f[1] for f in cds) <= v("vivienda", "permisos_12m"))
    nota = lagos["vivienda"]["tablas"]["permisos_por_distrito"].get("nota", "")
    sin = re.match(r"(\d+) permisos", nota)
    check("permisos · distritos + sin distrito = total exacto",
          sin and sum(f[1] for f in cds) + int(sin.group(1)) == v("vivienda", "permisos_12m"), nota)
if "movilidad" in lagos:
    check("bicis · operando <= estaciones", v("movilidad", "estaciones_operando") <= v("movilidad", "estaciones"))
    check("bicis · eléctricas <= disponibles", v("movilidad", "bicis_electricas") <= v("movilidad", "bicis_disponibles"))

# Natalidad y población por distrito (F07) y tasas per cápita
if "demografia" in lagos:
    tb = lagos["demografia"]["tablas"]
    pd = {f[0]: f[1] for f in tb["poblacion_por_distrito"]["filas"]}
    check("población por distrito · distritos 1 a 15", sorted(pd) == list(range(1, 16)), sorted(pd))
    check("población por distrito · suma cerca de la población de la ciudad (±2 %)",
          abs(sum(pd.values()) - v("demografia", "poblacion")) / v("demografia", "poblacion") < 0.02,
          (sum(pd.values()), v("demografia", "poblacion")))
    check("población por distrito · cada distrito entre 200.000 y 300.000", all(200_000 < n < 300_000 for n in pd.values()))
    check("población por distrito · la nota dice el método y el error",
          "Método" in tb["poblacion_por_distrito"].get("nota", "") and "Error" in tb["poblacion_por_distrito"]["nota"])
    nat = {f[0]: f for f in tb["natalidad_por_ambito"]["filas"]}
    check("natalidad · ciudad, California y EE. UU.",
          sorted(nat) == sorted(["Ciudad de Los Ángeles", "California", "Estados Unidos"]), sorted(nat))
    check("natalidad · nacimientos por 1.000 mujeres recalculado y en rango (10 a 100)",
          all(abs(f[3] - 1000 * f[2] / f[1]) < 0.06 and 10 < f[3] < 100 for f in nat.values()))
    check("natalidad · cifra de la ciudad igual a la de la tabla",
          v("demografia", "natalidad_ciudad_por_1000") == nat["Ciudad de Los Ángeles"][3])
    ser = tb["natalidad_serie_ciudad"]["filas"]
    check("natalidad · serie de la ciudad con 2 o más lanzamientos, ordenada y sin repetir",
          len(ser) >= 2 and [f[0] for f in ser] == sorted({f[0] for f in ser}))
    check("natalidad · último lanzamiento de la serie igual a la tabla comparada",
          ser[-1][3] == nat["Ciudad de Los Ángeles"][3])
    nd = tb.get("natalidad_por_distrito")
    check("natalidad por distrito · tabla presente", nd is not None)
    if nd:
        fd = nd["filas"]
        check("natalidad por distrito · distritos 1 a 15", sorted(f[0] for f in fd) == list(range(1, 16)))
        check("natalidad por distrito · tasa recalculada y en rango (10 a 100)",
              all(abs(f[3] - 1000 * f[2] / f[1]) < 0.06 and 10 < f[3] < 100 for f in fd))
        c = nat["Ciudad de Los Ángeles"]
        for i, nombre in ((1, "mujeres de 15 a 50"), (2, "nacimientos")):
            s = sum(f[i] for f in fd)
            check(f"natalidad por distrito · suma de {nombre} cerca de la ciudad en el mismo ACS (±1 %)",
                  abs(s - c[i]) / c[i] < 0.01, (s, c[i]))
        check("natalidad por distrito · mismo lanzamiento que la cifra de la ciudad",
              nd["vigencia"] == tb["natalidad_por_ambito"]["vigencia"])
        check("natalidad por distrito · la nota dice el método y el error", "Método" in nd.get("nota", "") and "Error" in nd["nota"])
    lic = next(f["licencia"] for f in lagos["demografia"]["fuentes"] if f["id"] == "F07")
    check("F07 · licencia con atribución exigida por el Censo", "not endorsed or certified" in lic, lic)
    for tema, clave, cols in (("municipio", "solicitudes_por_distrito", {"solicitudes": "solicitudes_por_10mil"}),
                              ("vivienda", "permisos_por_distrito", {"permisos": "permisos_por_10mil",
                                                                     "unidades_netas": "unidades_netas_por_10mil"})):
        t = lagos[tema]["tablas"][clave]
        ok = all(abs(f[t["columnas"].index(tasa)] - 10000 * f[t["columnas"].index(base)] / pd[f[0]]) < 0.06
                 for f in t["filas"] for base, tasa in cols.items())
        check(f"{tema} · tasas por 10.000 habitantes recalculadas con la población por distrito", ok)

# Ciclo de vida: un tema probado hace más de un año se declara vencido
hoy = datetime.date.today()
for tema, lago in lagos.items():
    dias = (hoy - datetime.date.fromisoformat(lago["probado"])).days
    check(f"{tema}: probado hace menos de un año", dias <= 365, f"{dias} días")

territorio = RAIZ / "territorio" / "distritos_consejo.geojson"
if territorio.exists():
    g = json.load(open(territorio, encoding="utf-8"))
    check("territorio: 15 distritos con cd y geometría",
          sorted(f["properties"]["cd"] for f in g["features"]) == list(range(1, 16))
          and all(f["geometry"]["type"] in ("Polygon", "MultiPolygon") for f in g["features"]))
    check("territorio: nota de simplificación y vigencia en cada distrito",
          "simplificada" in g.get("nota", "") and all(
              re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(f["properties"].get("vigencia"))) for f in g["features"]))

print(f"\n{fallos} fallos")
sys.exit(1 if fallos else 0)
