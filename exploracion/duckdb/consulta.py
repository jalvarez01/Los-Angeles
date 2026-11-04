"""Exploración con DuckDB sobre los mismos datos del lago (tramos de ingesta y de verificación).

Corre en un entorno virtual aparte, nunca en el del proyecto (el proyecto es solo biblioteca estándar):
    python3 -m venv exploracion/duckdb/.venv
    exploracion/duckdb/.venv/bin/pip install duckdb==2.0.0
    exploracion/duckdb/.venv/bin/python exploracion/duckdb/consulta.py
"""
import json
import pathlib

import duckdb

RAIZ = pathlib.Path(__file__).resolve().parents[2]
LAGO = RAIZ / "lago"
escucha = json.loads((LAGO / "escucha.json").read_text(encoding="utf-8"))
url = escucha["fuentes"][0]["url"]  # la misma consulta que hizo ingesta/pull_escucha.py (F11)

print("== Ingesta: DuckDB lee la API de Wikipedia (F11) directo desde la URL, sin bajarla a disco")
filas = duckdb.sql(f"""
    SELECT substr(i.timestamp, 1, 4) || '-' || substr(i.timestamp, 5, 2) AS mes, i.views AS vistas
    FROM (SELECT unnest(items) AS i FROM read_json_auto('{url}'))
    ORDER BY mes""").fetchall()
ultimo = escucha["series"]["vistas_mensuales"]["puntos"][-1]
print(f"   {len(filas)} meses; último {filas[-1]} · en el lago: {ultimo} · iguales: {list(filas[-1]) == ultimo}")

print("== Verificación: dos comprobaciones de verificar.py reescritas en SQL sobre lago/seguridad.json")
seg = str(LAGO / "seguridad.json")
total = duckdb.sql(f"SELECT cifras.delitos_12m.valor FROM read_json_auto('{seg}')").fetchall()[0][0]  # DuckDB 2.0 quitó fetchone() de las relaciones
suma_areas = duckdb.sql(f"""
    SELECT sum(CAST(f[2] AS BIGINT)) FROM (SELECT unnest(tablas.delitos_por_area.filas) AS f FROM read_json_auto('{seg}'))""").fetchall()[0][0]
print(f"   las áreas suman el total: {suma_areas} == {total} → {suma_areas == total}")
pequenas = duckdb.sql(f"""
    SELECT count(*) FROM (SELECT unnest(tablas.delitos_por_distrito_reporte.filas) AS f FROM read_json_auto('{seg}'))
    WHERE TRY_CAST(f[3] AS BIGINT) BETWEEN 1 AND 9""").fetchall()[0][0]
print(f"   conteos guardados entre 1 y 9 por distrito de reporte: {pequenas} (debe ser 0)")
print("duckdb", duckdb.__version__)
