#!/usr/bin/env python3
"""Ingesta F06 · Población y viviendas de la ciudad (California DOF, informe E-1) -> lago/demografia.json

El Excel trae DOS filas llamadas «Los Angeles»: el condado (~9,8 millones) y la ciudad (~3,8 millones).
Un título que coincide no es la cosa: se exige que haya exactamente dos y se toma la ciudad.
El DOF publica cada mayo; al salir el informe nuevo se cambia ANIO.
"""
import io
import re
import zipfile
import xml.etree.ElementTree as ET

from _comun import escribir_lago, get_bytes

ANIO = 2026
URL = ("https://dof.ca.gov/media/docs/forecasting/Demographics/estimates-e1/"
       f"E-1_{ANIO}_InternetVersion.xlsx")
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


def hojas(xlsx):
    """Lee un .xlsx con la biblioteca estándar: {nombre de hoja: [[celdas de la fila]]}."""
    z = zipfile.ZipFile(io.BytesIO(xlsx))
    textos = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS):
            textos.append("".join(t.text or "" for t in si.iter(f"{{{NS['m']}}}t")))
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    salida = {}
    for s in ET.fromstring(z.read("xl/workbook.xml")).find("m:sheets", NS):
        destino = rels[s.get(f"{{{NS['r']}}}id")].lstrip("/")
        destino = destino if destino.startswith("xl/") else "xl/" + destino
        filas = []
        for row in ET.fromstring(z.read(destino)).iter(f"{{{NS['m']}}}row"):
            fila = {}
            for c in row.findall("m:c", NS):
                col = re.match(r"[A-Z]+", c.get("r")).group()
                v = c.find("m:v", NS)
                if c.get("t") == "s":
                    val = textos[int(v.text)]
                elif c.get("t") == "inlineStr":
                    val = "".join(t.text or "" for t in c.iter(f"{{{NS['m']}}}t"))
                else:
                    val = v.text if v is not None else None
                fila[col] = val
            filas.append(fila)
        salida[s.get("name")] = filas
    return salida


def ciudad(filas):
    la = [f for f in filas if (f.get("A") or "").strip() == "Los Angeles"]
    assert len(la) == 2, f"se esperaban 2 filas «Los Angeles» (condado y ciudad), hay {len(la)}"
    return min(la, key=lambda f: float(f["C"]))  # la ciudad es la menor de las dos


libro = hojas(get_bytes(URL))
pob = ciudad(libro[f"E-1 CityCounty{ANIO}"])
viv = ciudad(libro[f"E-1H CityCounty{ANIO}"])

ahora, antes = f"{ANIO}-01-01", f"{ANIO - 1}-01-01"
escribir_lago(
    "demografia",
    fuentes=[{"id": "F06", "nombre": f"California DOF · E-1 Population and Housing Estimates {ANIO}",
              "url": URL, "estado": "vivo", "licencia": "no declara"}],
    cifras={
        "poblacion": {"valor": int(float(pob["C"])), "unidad": "habitantes", "vigencia": ahora, "fuente": "F06"},
        "poblacion_anio_anterior": {"valor": int(float(pob["B"])), "unidad": "habitantes",
                                    "vigencia": antes, "fuente": "F06"},
        "variacion_poblacion_pct": {"valor": round(float(pob["D"]), 2), "unidad": "% anual",
                                    "vigencia": f"{antes} a {ahora}", "fuente": "F06"},
        "viviendas": {"valor": int(float(viv["C"])), "unidad": "unidades de vivienda",
                      "vigencia": ahora, "fuente": "F06"},
    },
    fusionar=True,
)
