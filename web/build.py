#!/usr/bin/env python3
"""Arma web/dist: la página más una copia de lago/ y territorio/ (solo biblioteca estándar)."""
import pathlib
import shutil

WEB = pathlib.Path(__file__).resolve().parent
RAIZ = WEB.parent
DIST = WEB / "dist"
shutil.rmtree(DIST, ignore_errors=True)
DIST.mkdir()
shutil.copy(WEB / "index.html", DIST / "index.html")
for carpeta in ("lago", "territorio"):
    shutil.copytree(RAIZ / carpeta, DIST / carpeta, ignore=shutil.ignore_patterns("raw"))
print(f"escrito {DIST.relative_to(RAIZ)}")
