#!/usr/bin/env python3

"""
Stokmont final XML'ine <Gtin> alanını ekler.
Değerleri kaynak XML'deki <Gtin> ve <VariantGtin>'den alır,
WG'yi SD'ye değiştirir.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Dict

FINAL_XML = "stokmont_final_sdstep_titles_buyingprice_barcode_pretty.xml"
SOURCE_XML = "wagoon_source_pretty.xml"


def load_source_gtins() -> Dict[str, Dict[str, str]]:
    """Kaynak XML'den ProductCode -> {'product_gtin': ..., 'variant_gtins': {VariantCode: gtin}} çıkarır."""
    try:
        tree = ET.parse(SOURCE_XML)
    except Exception:
        return {}

    root = tree.getroot()
    mapping: Dict[str, Dict[str, str]] = {}
    for p in root.findall("Product"):
        code_el = p.find("ProductCode")
        if code_el is None or code_el.text is None or not code_el.text.strip():
            continue
        code = code_el.text.strip()

        gtin_el = p.find("Gtin")
        product_gtin = gtin_el.text.strip() if gtin_el is not None and gtin_el.text is not None else ""

        variant_gtins: Dict[str, str] = {}
        for v in p.findall("Variants/Variant"):
            v_code_el = v.find("VariantCode")
            v_gtin_el = v.find("VariantGtin")
            if v_code_el is not None and v_code_el.text is not None and v_gtin_el is not None and v_gtin_el.text is not None:
                v_code = v_code_el.text.strip()
                v_gtin = v_gtin_el.text.strip()
                variant_gtins[v_code] = v_gtin

        mapping[code] = {"product_gtin": product_gtin, "variant_gtins": variant_gtins}
    return mapping


def add_gtins():
    src_gtins = load_source_gtins()
    print(f"Loaded {len(src_gtins)} products from source")

    tree = ET.parse(FINAL_XML)
    root = tree.getroot()

    for p in root.findall("Product"):
        code_el = p.find("ProductCode")
        if code_el is None or code_el.text is None or not code_el.text.strip():
            continue
        code = code_el.text.strip()

        # SD'ye çevir
        wg_code = code.replace("SD-", "WG-")
        src_data = src_gtins.get(wg_code, {})
        product_gtin = src_data.get("product_gtin", "")
        if product_gtin:
            product_gtin = product_gtin.replace("WG", "SD", 1)  # Sadece başındaki WG'yi SD'ye
            gtin_el = ET.SubElement(p, "Gtin")
            gtin_el.text = product_gtin

        # Variant'lar için
        for v in p.findall("Variants/Variant"):
            v_code_el = v.find("VariantCode")
            if v_code_el is None or v_code_el.text is None or not v_code_el.text.strip():
                continue
            v_code = v_code_el.text.strip()
            wg_v_code = v_code.replace("SD-", "WG-")
            variant_gtins = src_data.get("variant_gtins", {})
            v_gtin = variant_gtins.get(wg_v_code, "")
            if v_gtin:
                v_gtin = v_gtin.replace("WG", "SD", 1)
                v_gtin_el = ET.SubElement(v, "Gtin")
                v_gtin_el.text = v_gtin

    # Pretty print
    try:
        ET.indent(tree, space="  ")
    except Exception:
        pass

    tree.write(FINAL_XML, encoding="utf-8", xml_declaration=True)

    print("GTIN alanları eklendi ve WG -> SD dönüştürüldü.")


if __name__ == "__main__":
    try:
        add_gtins()
    except Exception as e:
        print(f"Hata: {e}")