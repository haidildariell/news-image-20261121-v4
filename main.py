#!/usr/bin/env python3
"""Entry point for the news-image-20261121 v4 front page.

The picture itself is drawn by build_image.py (Pillow) and stored in
this repository as entry.png. This module is deliberately
standard-library-only: it just places that file where the harness
expects it, so the program is deterministic and needs no network.

Run it with ``python3 main.py``. The harness sets MAKEFUN_OUTPUT_DIR;
without it, the image goes to /output, matching the kit contract.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE_NAME = "entry.png"
DEFAULT_OUTPUT_DIR = "/output"


def _output_dir():
    """Where the harness wants the image (env override, else /output)."""
    wanted = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if wanted:
        return wanted
    return DEFAULT_OUTPUT_DIR


def place_image():
    """Copy entry.png into the output directory, creating it if needed."""
    src = os.path.join(HERE, SOURCE_NAME)
    dest_dir = _output_dir()
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, SOURCE_NAME)
    shutil.copyfile(src, dest)
    return dest


if __name__ == "__main__":
    placed = place_image()
    print("entry.png ->", placed)
