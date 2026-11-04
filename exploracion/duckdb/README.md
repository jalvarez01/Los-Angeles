# DuckDB 2.0.0 (tramos de ingesta y verificación)

Cómo correrlo: `python3 -m venv exploracion/duckdb/.venv && exploracion/duckdb/.venv/bin/pip install duckdb==2.0.0 && exploracion/duckdb/.venv/bin/python exploracion/duckdb/consulta.py`. `salida.txt` es la salida real del 2026-11-03. Al leer la URL, DuckDB descarga solo la extensión httpfs (19,7 MB) en `~/.duckdb/extensions`, fuera del entorno virtual.
