#!/usr/bin/env python3
"""把编译好的 PDF 渲染成一张缩略图拼图，一次看完所有页；同时列出编译日志里的溢出警告。
用法：python3 contact_sheet.py presentation.pdf [--cols 4] [--dpi 45] [--log build/presentation.log] [--out contact.png]
需要 poppler（pdftoppm）和 Pillow。看细节时单页放大：pdftoppm -png -r 90 -f N -l N presentation.pdf page"""
import argparse, glob, os, re, subprocess, tempfile
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("pdf")
ap.add_argument("--cols", type=int, default=4)
ap.add_argument("--dpi", type=int, default=45)
ap.add_argument("--log", help="编译日志；默认找 build/<名>.log 或 <名>.log")
ap.add_argument("--out", help="默认 <pdf 名>_contact.png")
a = ap.parse_args()

stem = os.path.splitext(a.pdf)[0]
with tempfile.TemporaryDirectory() as d:
    subprocess.run(["pdftoppm", "-png", "-r", str(a.dpi), a.pdf, f"{d}/p"], check=True)
    ims = [Image.open(f) for f in sorted(glob.glob(f"{d}/p-*.png"))]
    w, h = ims[0].size
    rows = (len(ims) + a.cols - 1) // a.cols
    sheet = Image.new("RGB", (w * a.cols, h * rows), "white")
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % a.cols) * w, (i // a.cols) * h))
    out = a.out or f"{stem}_contact.png"
    sheet.save(out)
print(f"{len(ims)} 页 → {out}")

log = a.log or next((p for p in (f"{os.path.dirname(a.pdf) or '.'}/build/{os.path.basename(stem)}.log", f"{stem}.log")
                     if os.path.exists(p)), None)
if log:
    warn = [l.strip() for l in open(log, errors="ignore") if re.match(r"(Overfull|^!)", l.strip())]
    print(f"{log}：{len(warn)} 处溢出 / 错误" + "".join(f"\n  {l}" for l in warn[:20]))
