#!/usr/bin/env python3
"""
Generate synthetic EAN-13-like numeric barcodes for Trendyol/Hepsiburada compatibility.

Behaviour:
- Read an input Stokmont XML (Products/Product/Variants/Variant...)
- For each Product, if <Barcode> exists and contains digits, keep it; otherwise generate a new 13-digit EAN-like barcode.
- For each Variant, if it has a <Barcode> child, keep it; otherwise set the Variant-level barcode to the product barcode + a small suffix and recalc checksum.
- Write two outputs: raw XML and pretty-printed XML.

Usage: python make_synthetic_barcodes.py 
Defaults read: stokmont_final_sdstep_titles_buyingprice_pretty.xml
Outputs: stokmont_final_sdstep_titles_buyingprice_barcode.xml and ..._pretty.xml
"""
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom
import random
import re
from datetime import date


def ean13_checksum(number12: str) -> str:
    """Compute EAN-13 checksum for 12-digit string; returns single digit as string."""
    assert len(number12) == 12 and number12.isdigit()
    total = 0
    for i, ch in enumerate(number12):
        digit = int(ch)
        if (i % 2) == 0:
            total += digit
        else:
            total += 3 * digit
    check = (10 - (total % 10)) % 10
    return str(check)


def generate_base_ean(prefix_digits: str = None) -> str:
    """Generate a 13-digit EAN-13. If prefix_digits given, use its leading digits (max 12)."""
    # Her çağrıda tamamen rastgele 12 hane üret
    twelve = ""
    for _ in range(12):
        twelve += str(random.randint(0, 9))
    return twelve + ean13_checksum(twelve)


def pretty_write(elem: ET.Element, path: str):
    s = ET.tostring(elem, encoding='utf-8')
    parsed = minidom.parseString(s)
    pretty_xml = parsed.toprettyxml(indent='  ', encoding='utf-8').decode('utf-8')
    # Remove extra blank lines
    lines = [line for line in pretty_xml.split('\n') if line.strip()]
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def main():
    in_file = 'stokmont_final_sdstep_titles_buyingprice_pretty.xml'
    out_file = 'stokmont_final_sdstep_titles_buyingprice_barcode.xml'
    out_pretty = 'stokmont_final_sdstep_titles_buyingprice_barcode_pretty.xml'

    if len(sys.argv) >= 2:
        in_file = sys.argv[1]
    if len(sys.argv) >= 3:
        out_file = sys.argv[2]
    if len(sys.argv) >= 4:
        out_pretty = sys.argv[3]

    tree = ET.parse(in_file)
    root = tree.getroot()

    product_count = 0
    generated = 0

    used_barcodes = set()
    for p in root.findall('Product'):
        product_count += 1
        # Her ürün için yeni benzersiz barcode üret
        while True:
            product_barcode = generate_base_ean()
            if product_barcode not in used_barcodes:
                used_barcodes.add(product_barcode)
                break
        bc = p.find('Barcode')
        if bc is None:
            bc = ET.SubElement(p, 'Barcode')
        bc.text = product_barcode
        generated += 1

        # Her varyant için de benzersiz barcode üret
        variants = p.find('Variants')
        if variants is not None:
            for v in variants.findall('Variant'):
                while True:
                    vbarcode = generate_base_ean()
                    if vbarcode not in used_barcodes:
                        used_barcodes.add(vbarcode)
                        break
                vbc = v.find('Barcode')
                if vbc is None:
                    vbc = ET.SubElement(v, 'Barcode')
                vbc.text = vbarcode
                generated += 1

    # write raw
    tree.write(out_file, encoding='utf-8', xml_declaration=True)
    # pretty
    pretty_write(root, out_pretty)

    print(f'Products processed: {product_count}, barcodes generated: {generated}')


if __name__ == '__main__':
    main()
