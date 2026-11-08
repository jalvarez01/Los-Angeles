"""Exploración del tramo «Contrato»: JSON Schema (check-jsonschema) frente a verificacion/verificar.py.

1. Valida los siete archivos reales de lago/ contra esquema.json.
2. Rompe una copia del lago (en un directorio temporal, fuera del repo) de cuatro maneras y anota qué atrapa cada herramienta.
Corre con el python del entorno aparte:  exploracion/contrato/.venv/bin/python exploracion/contrato/prueba.py
"""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
CHECK = AQUI / ".venv" / "bin" / "check-jsonschema"
ESQUEMA = AQUI / "esquema.json"
salida = []


def di(*x):
    print(*x); salida.append(" ".join(str(v) for v in x))


def esquema(archivos):
    r = subprocess.run([str(CHECK), "--schemafile", str(ESQUEMA), *map(str, archivos)], capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def verificador(raiz):
    r = subprocess.run([sys.executable, str(raiz / "verificacion" / "verificar.py")], capture_output=True, text=True)
    fallas = [l for l in r.stdout.splitlines() if l.startswith("FAIL")]
    return r.returncode, fallas


lagos = sorted((RAIZ / "lago").glob("*.json"))
di("== 1. Los siete archivos reales del lago contra esquema.json")
codigo, texto = esquema(lagos)
di(f"check-jsonschema: código {codigo}"); di(texto)

ROTURAS = {
    "a) una cifra sin vigencia": ("municipio", lambda d: d["cifras"]["solicitudes_anio"].pop("vigencia")),
    "b) una fila de tabla con una columna de menos": ("municipio", lambda d: d["tablas"]["solicitudes_por_distrito"]["filas"][0].pop()),
    "c) una cifra cuya fuente (F99) no está en fuentes": ("vivienda", lambda d: d["cifras"]["permisos_12m"].update(fuente="F99")),
    "d) un conteo de 5 ofensas guardado en un distrito de reporte": ("seguridad", lambda d: (lambda f: (f.__setitem__(2, 5), f.__setitem__(3, False)))(
        next(f for f in d["tablas"]["delitos_por_distrito_reporte"]["filas"] if f[3]))),
}
di("\n== 2. Roturas a propósito en una copia del lago: ¿quién las atrapa?")
for nombre, (tema, romper) in ROTURAS.items():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        for carpeta in ("lago", "territorio", "verificacion"):
            shutil.copytree(RAIZ / carpeta, tmp / carpeta, ignore=shutil.ignore_patterns("raw", "__pycache__"))
        p = tmp / "lago" / f"{tema}.json"
        d = json.loads(p.read_text(encoding="utf-8")); romper(d); p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        ce, te = esquema([p])
        te = te.replace(str(tmp), "copia")
        cv, fv = verificador(tmp)
        di(f"{nombre}:")
        di(f"   esquema:     {'ATRAPA' if ce else 'no lo ve'}" + (f" · {te.splitlines()[-1].strip()[:140]}" if ce else ""))
        di(f"   verificador: {'ATRAPA' if cv else 'no lo ve'}" + (f" · {fv[0][:140]}" if fv else ""))

(AQUI / "salida.txt").write_text("\n".join(salida) + "\n", encoding="utf-8")
