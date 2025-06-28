# 📄 pdf2seg

**Tokenizer-free PDF segmentation using OCR and span-aware text chunking.**

`pdf2seg` processes scanned or embedded-text PDFs using EasyOCR and spaCy, segmenting raw text into semantically relevant spans—no tokenizers, sentence splitters, or fixed rules required.

---

## 🚀 Features

- **Tokenizer-Free Chunking** – no subword vocabularies or fragile heuristics
- **OCR-Agnostic** – supports scanned PDFs with diagrams, math, or multilingual text
- **Span-Aware Segmentation** – uses spaCy syntax and entropy-minimized sampling
- **Checkpointing & Resume Support** – deterministic processing saved to `hash.json`
- **Rich Console UI** – interactive UV-style bars powered by `rich`

---

## 📦 Installation

Install from PyPI:

```bash
pip install pdf2seg
```

Or with [UV](https://github.com/astral-sh/uv):

```bash
uv pip install pdf2seg
```

---

## 🧪 Quick Usage

```bash
pdf2seg -i paper.pdf -o data/
```

📁 Output:
```
data/
|── <hash>/
|   |── <hash>-p000.png  ← rendered page
|   |── <hash>-p000.txt  ← OCR result
|   |── <hash>.json      ← processing manifest
|── <hash>.csv           ← segmented spans
```

---

## 🧬 Internals

Under the hood, `pdf2seg` performs:

1. PDF-to-image conversion (`pdf2image`)
2. OCR with `easyocr`
3. Sentence splitting + span grouping with `spacy`
4. Filtering + export to CSV
5. Manifest updates for resumability

You can inspect the span cutoff logic, filters, or tweak the entropy mode in `__init__.py`.

---

## 🧩 Future Plans

- Modality tagging (code vs prose vs formulae)
- Math-aware OCR fallback (e.g. Im2LaTeX)
- Stream-aware recomposition
- Standalone `hash-viewer` web demo

---

## 🔖 License

MIT License © 2025 Rawson, Kara  
Project: [p3nGu1nZz/pdf2seg](https://github.com/p3nGu1nZz/pdf2seg)

---

If you use or reference this software in an academic publication or project, please consider citing it using the following BibTeX entry:

```bibtex
@software{rawson2025pdf2seg,
  author       = {Rawson, Kara},
  title        = {pdf2seg: Tokenizer-Free PDF Segmentation with OCR and Span-Aware Chunking},
  year         = {2025},
  version      = {1.0.1},
  url          = {https://github.com/p3nGu1nZz/pdf2seg},
  note         = {Python package available at PyPI: https://pypi.org/project/pdf2seg/}
}
```

---

## 👁 See Also

- [X-Spanformer: Tokenizer-Free Span Induction with Structural Fusion](https://zenodo.org/records/15750962)  
- [oxbar](https://github.com/p3nGu1nZz/oxbar): Compile structured span labels with local LLMs
