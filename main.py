#!/usr/bin/env python3
"""Entrypoint for the make.fun news-image-20261121 v4 entry.

Copies the pre-rendered entry.png into the harness output directory.
Build the image first with:  python3 build_image.py
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

os.makedirs(OUT, exist_ok=True)
shutil.copyfile(os.path.join(HERE, "entry.png"),
                os.path.join(OUT, "entry.png"))
print("entry.png ->", os.path.join(OUT, "entry.png"))
