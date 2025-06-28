import csv, hashlib, json, random, easyocr, spacy, numpy as np
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict
from PIL import Image
from pdf2image import convert_from_path
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich.text import Text
from spacy.cli.download import download
from spacy.util import is_package

DPI, MIN, MAX, LM, LANG, GPU = 300, 1, 5, "en_core_web_sm", ['en'], True
C = Console()

load = lambda m=LM: (
    spacy.load(m) if is_package(m)
    else (C.print(Text(f"[boot] Installing {m}", style="yellow"))
    or download(m) or spacy.load(m))
)

def bar(task):
    return Progress(
        TextColumn(f"[bold blue]{task}"),
        BarColumn(bar_width=None),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        expand=True,
        console=C,
    )

def cut(txt, nlp, a=MIN, b=MAX):
    s = [x.text.strip() for x in nlp(txt).sents if x.text.strip()]
    out, i = [], 0
    while i < len(s):
        k = random.randint(a, b)
        out.append(" ".join(s[i:i+k]))
        i += k
    return out

def hash(p): return hashlib.sha256(Path(p).name.encode()).hexdigest()[:8]

def state(dir: Path) -> Dict[str, Any]:
    f = dir / f"{dir.name}.json"
    if not f.exists(): return {"ocr": [], "rendered": False, "pages": 0}
    try:
        s = json.loads(f.read_text("utf-8"))
        return s if isinstance(s, dict) else {"ocr": [], "rendered": False, "pages": 0}
    except Exception:
        return {"ocr": [], "rendered": False, "pages": 0}

def save(dir: Path, d: Dict[str, Any]):
    (dir / f"{dir.name}.json").write_text(json.dumps(d, indent=2), encoding="utf-8")

def pdf(p: str, d: Path, dpi=DPI):
    d.mkdir(parents=True, exist_ok=True)
    meta: Dict[str, Any] = state(d)
    img = list(d.glob(f"{d.name}-p*.png"))
    if meta.get("rendered") and len(img) == meta.get("pages", 0):
        return sorted(img), meta
    pages = convert_from_path(str(p), dpi=dpi)
    meta["pages"] = len(pages)
    with bar("📄 Rendering PDF") as prog:
        task = prog.add_task("", total=len(pages))
        for i, im in enumerate(pages):
            fn = d / f"{d.name}-p{i:03}.png"
            if not fn.exists(): im.save(fn, "PNG")
            prog.update(task, advance=1)
    meta["rendered"] = True
    save(d, meta)
    return sorted(d.glob(f"{d.name}-p*.png")), meta

def ocr(imgs, meta: Dict[str, Any], d: Path):
    txts, R = [], easyocr.Reader(LANG, gpu=GPU)
    with bar("🔍 OCR Progress") as prog:
        task = prog.add_task("", total=len(imgs))
        for i, fn in enumerate(imgs):
            pid = f"{d.name}-p{i:03}"
            txt = d / f"{pid}.txt"
            if i in meta.get("ocr", []) and txt.exists():
                txts.append(txt.read_text("utf-8"))
                prog.update(task, advance=1)
                continue
            arr = np.array(Image.open(fn))
            lines = [x.strip() for x in R.readtext(arr, detail=0, paragraph=True)
                     if isinstance(x, str) and x.strip()]
            txt.write_text("\n".join(lines), encoding="utf-8")
            meta.setdefault("ocr", []).append(i)
            save(d, meta)
            txts.append("\n".join(lines))
            prog.update(task, advance=1)
    return txts

def filt(spans, nlp, min_len=24, min_words=4):
    keep = []
    for s in spans:
        doc = nlp(s)
        if len(s.strip()) < min_len: continue
        if sum(t.is_alpha for t in doc) < min_words:
            if not any(c.isnumeric() or c in "=/^*%$" for c in s): continue
        keep.append(s)
    return keep

def save_csv(spans, out, src, meta: Dict[str, Any]):
    out = Path(out)
    name = hash(src)
    dest = out / f"{name}.csv" if out.is_dir() else out
    dest.parent.mkdir(parents=True, exist_ok=True)
    C.print(Text(f"💾 Writing {len(spans)} spans → {dest}", style="blue"))
    with bar("✨ Saving CSV") as prog:
        task = prog.add_task("", total=len(spans))
        with open(dest, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["id", "text"])
            for i, s in enumerate(spans, 1):
                w.writerow([i, s])
                prog.update(task, advance=1)
    meta.update({
        "csv": str(dest),
        "spans": len(spans),
        "chars": sum(len(s) for s in spans),
        "modified": datetime.now(UTC).isoformat()
    })
    save(Path(out) / hash(src), meta)

def extract(input_path: str, output_path: str, nlp):
    h = hash(input_path)
    d = Path(output_path) / h
    imgs, meta = pdf(input_path, d)
    raw = ocr(imgs, meta, d)
    spans = [s for t in raw for s in cut(t, nlp)]
    spans = filt(spans, nlp)
    save_csv(spans, output_path, input_path, meta)