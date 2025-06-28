import argparse
from . import load, extract

def main():
    p = argparse.ArgumentParser(prog="pdf2seg", description="PDF to OCR-based segment extractor")
    p.add_argument("-i", "--input", required=True, help="Input PDF file")
    p.add_argument("-o", "--output", required=True, help="Output directory")
    args = p.parse_args()
    nlp = load()
    extract(args.input, args.output, nlp)