#!/usr/bin/env python3

"""
Stokmont final XML içindeki <Category> alanları şu an HTML-escaped CDATA metni olarak yazılmış durumda:

  <Category>&lt;![CDATA[TERLİK]]&gt;</Category>

Bu durum, Stokmont kategori eşleştirme ekranında kategorilerin görünmemesine yol açabilir.
Bu script, tüm <Category> metinlerini şu formata dönüştürür:

  <Category>TERLİK</Category>

Ek olarak, eğer gelecekte bazı ürünlerde <Category> yoksa (edge case),
orijinal "wagoon_source_pretty.xml" içindeki CategoryName/CategoryPath bilgisine
ProductCode eşleşmesi (SD- -> WG- geri dönüşümü) ile ulaşmayı dener.
"""

from __future__ import annotations

import html
import sys
import xml.etree.ElementTree as ET
from typing import Dict

FINAL_XML = "stokmont_final_sdstep_titles_buyingprice_barcode_pretty.xml"
SOURCE_XML = "wagoon_source_pretty.xml"


def load_source_categories() -> Dict[str, Dict[str, str]]:
    """wagoon_source_pretty.xml içinden ProductCode -> {'path': CategoryPath, 'name': CategoryName} haritası çıkarır.

    Anahtar: WG-* ProductCode
    """
    try:
        tree = ET.parse(SOURCE_XML)
    except Exception:
        return {}

    root = tree.getroot()
    mapping: Dict[str, Dict[str, str]] = {}
    for p in root.findall("Product"):
        code_el = p.find("ProductCode")
        if code_el is None or not (code_el.text and code_el.text.strip()):
            continue
        code = code_el.text.strip()

        cats = p.find("Categories")
        if cats is not None:
            path_el = cats.find("CategoryPath")
            name_el = cats.find("CategoryName")
            path_val = path_el.text.strip() if path_el is not None and path_el.text else ""
            name_val = name_el.text.strip() if name_el is not None and name_el.text else ""
            if path_val or name_val:
                mapping[code] = {"path": path_val, "name": name_val}
    return mapping


def clean_cdata_text(text: str | None) -> str:
    if not text:
        return ""
    # Önce HTML entity'lerini çözelim (örn. &lt;![CDATA[TERLİK]]&gt; -> <![CDATA[TERLİK]]>)
    unescaped = html.unescape(text)
    u = unescaped.strip()
    # <![CDATA[...]]> kalıbı varsa içeriği al
    if u.startswith("<![CDATA[") and u.endswith("]]>"):
        return u[9:-3].strip()
    return u


def fix_categories():
    src_categories = load_source_categories()

    tree = ET.parse(FINAL_XML)
    root = tree.getroot()

    fixed_count = 0
    filled_from_src = 0
    empty_after_clean = 0

    for p in root.findall("Product"):
        code_el = p.find("ProductCode")
        code = code_el.text.strip() if code_el is not None and code_el.text else ""

        cat_el = p.find("Category")
        if cat_el is None:
            cat_el = ET.SubElement(p, "Category")

        cleaned = clean_cdata_text(cat_el.text)

        # Stokmont için MainCategory ve SubCategory ekle
        main_cat_el = p.find("MainCategory")
        if main_cat_el is None:
            main_cat_el = ET.SubElement(p, "MainCategory")

        sub_cat_el = p.find("SubCategory")
        if sub_cat_el is None:
            sub_cat_el = ET.SubElement(p, "SubCategory")

        if not cleaned:
            # Kaynaktan doldurmayı dene: SD- -> WG- çevir
            wg_code = code.replace("SD-", "WG-") if code else ""
            src_data = src_categories.get(wg_code, {})
            src_path = src_data.get("path", "")
            src_name = src_data.get("name", "")
            cat_val = src_path or src_name
            if cat_val:
                cat_el.text = cat_val
                cleaned = cat_val
                filled_from_src += 1
            else:
                cat_el.text = cleaned
                empty_after_clean += 1
        else:
            if cat_el.text != cleaned:
                cat_el.text = cleaned
                fixed_count += 1

        # MainCategory ve SubCategory'yi ayarla
        sub_cat = ""
        if cleaned:
            parts = cleaned.split("/", 1)  # İlk "/" ile ayır
            main_cat = parts[0].strip()
            sub_cat = parts[1].strip() if len(parts) > 1 else ""
        else:
            # Kaynaktan al
            wg_code = code.replace("SD-", "WG-") if code else ""
            src_data = src_categories.get(wg_code, {})
            src_path = src_data.get("path", "")
            if src_path:
                parts = src_path.split("/", 1)
                main_cat = parts[0].strip()
                sub_cat = parts[1].strip() if len(parts) > 1 else ""
            else:
                main_cat = ""

        # Description'dan alt kategori çıkar (ör. "Kategori: Erkek Ayakkabı")
        desc_el = p.find("Description")
        if desc_el is not None and desc_el.text:
            desc_text = html.unescape(desc_el.text)  # CDATA içinden çıkar
            if "Kategori:" in desc_text:
                start = desc_text.find("Kategori:") + len("Kategori:")
                end = desc_text.find("<br />", start)
                if end == -1:
                    end = len(desc_text)
                sub_from_desc = desc_text[start:end].strip()
                if sub_from_desc and not sub_cat:
                    sub_cat = sub_from_desc

        main_cat_el.text = main_cat
        sub_cat_el.text = sub_cat

    # Pretty print (Python 3.9+)
    try:
        ET.indent(tree, space="  ")
    except Exception:
        pass

    tree.write(FINAL_XML, encoding="utf-8", xml_declaration=True)

    print(
        f"Category düzeltildi: {fixed_count} | Kaynaktan doldurulan: {filled_from_src} | Boş kalan: {empty_after_clean}"
    )


if __name__ == "__main__":
    try:
        fix_categories()
    except Exception as e:
        print(f"Hata: {e}")
        sys.exit(1)
