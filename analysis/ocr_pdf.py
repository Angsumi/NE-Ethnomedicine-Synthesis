"""OCR a scanned PDF to text, keeping line order. usage: ocr_pdf.py in.pdf out.txt"""
import sys, pymupdf
from rapidocr_onnxruntime import RapidOCR
ocr = RapidOCR(); out = []
pages = set(range(int(sys.argv[3].split("-")[0]), int(sys.argv[3].split("-")[1]) + 1)) if len(sys.argv) > 3 else None
for i, page in enumerate(pymupdf.open(sys.argv[1])):
    if pages and i + 1 not in pages: continue
    img = page.get_pixmap(dpi=200).tobytes("png")
    res, _ = ocr(img)
    res = sorted(res or [], key=lambda r: (round(r[0][0][1] / 15), r[0][0][0]))
    lines, cur, y = [], [], None
    for box, txt, conf in res:
        yy = round(box[0][1] / 15)
        if y is not None and yy != y: lines.append("  ".join(cur)); cur = []
        cur.append(txt); y = yy
    if cur: lines.append("  ".join(cur))
    out.append(f"\n=== page {i+1} ===\n" + "\n".join(lines)); print("page", i + 1, len(res), file=sys.stderr)
open(sys.argv[2], "w").write("\n".join(out))
