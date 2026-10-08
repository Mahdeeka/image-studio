"""Rebuild dist/image-studio.zip, the file people upload in Claude under Customize > Skills.

Run after changing anything in plugins/image-studio/skills/image-studio:  python scripts/build_zip.py
"""
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "plugins", "image-studio", "skills", "image-studio")
OUT = os.path.join(ROOT, "dist", "image-studio.zip")
SKIP_DIRS = {"__pycache__", "out"}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for base, dirs, files in os.walk(SKILL):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for f in sorted(files):
            if f.endswith(".pyc") or f == ".DS_Store" or (f.startswith("_") and f.endswith((".html", ".png"))):
                continue
            p = os.path.join(base, f)
            z.write(p, os.path.join("image-studio", os.path.relpath(p, SKILL)).replace(os.sep, "/"))
print(OUT, f"{os.path.getsize(OUT) / 1e6:.1f} MB")
