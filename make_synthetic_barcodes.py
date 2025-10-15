#!/usr/bin/env python3
"""Generate synthetic barcodes/GTINs prefixed with 'SD' for stokmont final XML.

Reads: stokmont_final_sdstep_titles_buyingprice.xml
Writes:
 - stokmont_final_sdstep_titles_buyingprice_barcode.xml
 - stokmont_final_sdstep_titles_buyingprice_barcode_pretty.xml

Algorithm:
 - For each <Product>, replace <Barcode> value with SD{index}{ProductCode_clean}
 - Also replace any <Gtin> or <VariantGtin> tags if present (case-insensitive tag names handled)
 - Keep original format and other fields unchanged
 - Pretty-print output using xml.dom.minidom

This is idempotent if run repeatedly (it will overwrite with new SD values deterministically based on product order).
"""
import xml.etree.ElementTree as ET
from xml.dom import minidom
import re
import sys
from pathlib import Path

SRC = Path('stokmont_final_sdstep_titles_buyingprice.xml')
OUT = Path('stokmont_final_sdstep_titles_buyingprice_barcode.xml')
OUT_PRETTY = Path('stokmont_final_sdstep_titles_buyingprice_barcode_pretty.xml')

if not SRC.exists():
    print(f"Source file {SRC} not found. Run previous pipeline to create it.")
    sys.exit(1)

def clean_code(code: str) -> str:
    # Keep only ASCII alnum and hyphen
    return re.sub(r'[^A-Za-z0-9\-]', '', code or '')

tree = ET.parse(str(SRC))
root = tree.getroot()

product_nodes = root.findall('.//Product')
print(f'Found {len(product_nodes)} products')

for idx, p in enumerate(product_nodes, start=1):
    code_el = p.find('ProductCode')
    code = code_el.text if code_el is not None else f'X{idx}'
    code_clean = clean_code(code).upper()

    # Generate synthetic barcode value
    synthetic = f'SD{idx:05d}{code_clean}'

    # Replace Barcode if present
    barcode_el = p.find('Barcode')
    if barcode_el is not None:
        barcode_el.text = synthetic

    # Replace any Gtin/VariantGtin tags (case-insensitive)
    for child in list(p):
        tag = child.tag.lower()
        if 'gtin' in tag or 'gtin' == tag or tag == 'variantgtin' or tag == 'gtin13':
            child.text = synthetic

    # Also scan Variants for VariantBarcode/VariantGtin
    variants = p.find('Variants')
    if variants is not None:
        for v in variants.findall('.//Variant'):
            vb = v.find('VariantBarcode')
            if vb is not None:
                vb.text = synthetic
            vg = v.find('VariantGtin')
            if vg is not None:
                vg.text = synthetic

# Write raw output
tree.write(str(OUT), encoding='utf-8', xml_declaration=True)

# Pretty-print
xml_str = OUT.read_text(encoding='utf-8')
parsed = minidom.parseString(xml_str)
pretty = parsed.toprettyxml(indent='  ', encoding='utf-8')
OUT_PRETTY.write_bytes(pretty)

print(f'Wrote {OUT} and {OUT_PRETTY}')
