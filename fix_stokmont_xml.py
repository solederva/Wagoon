#!/usr/bin/env python3
"""
Stokmont'a uygun XML formatına dönüştürme scripti.
Stokmont'a gönderilen XML üzerinden gerekli düzenlemeleri yapar.
"""

import xml.etree.ElementTree as ET
import html
import re

def fix_stokmont_xml(input_file, output_file):
    """Stokmont'a uygun XML formatına dönüştürür"""

    print("🔧 Stokmont XML Format Düzeltmesi Başlıyor...")
    print("=" * 50)

    tree = ET.parse(input_file)
    root = tree.getroot()

    product_count = 0
    fixes_applied = {
        'description_cleaned': 0,
        'gtin_fixed': 0,
        'category_fixed': 0,
        'encoding_fixed': 0
    }

    for product in root.findall('.//Product'):
        product_count += 1

        # 1. Description'ı düz metin yap (CDATA olmadan)
        desc_elem = product.find('Description')
        if desc_elem is not None and desc_elem.text:
            # CDATA içindeki HTML'i temizle
            if '<![CDATA[' in desc_elem.text:
                # CDATA içeriğini çıkar
                cdata_match = re.search(r'<!\[CDATA\[(.*?)\]\]>', desc_elem.text, re.DOTALL)
                if cdata_match:
                    html_content = cdata_match.group(1)
                    # HTML entity'leri decode et
                    clean_text = html.unescape(html_content)
                    # Gereksiz tag'leri temizle (sadece temel metin bırak)
                    clean_text = re.sub(r'<[^>]+>', '', clean_text)
                    # Fazla boşlukları temizle
                    clean_text = ' '.join(clean_text.split())
                    desc_elem.text = clean_text
                    fixes_applied['description_cleaned'] += 1

        # 2. GTIN formatını düzelt (SD prefix olmadan sadece sayısal)
        gtin_elem = product.find('Gtin')
        if gtin_elem is not None and gtin_elem.text and gtin_elem.text.startswith('SD'):
            # SD prefix'ini kaldır, sadece sayısal kısım
            numeric_gtin = re.sub(r'[^0-9]', '', gtin_elem.text)
            if len(numeric_gtin) >= 13:
                gtin_elem.text = numeric_gtin[:13]  # İlk 13 rakamı al
                fixes_applied['gtin_fixed'] += 1

        # 3. Variant GTIN'lerini de düzelt
        variants = product.find('Variants')
        if variants is not None:
            for variant in variants.findall('Variant'):
                v_gtin_elem = variant.find('Gtin')
                if v_gtin_elem is not None and v_gtin_elem.text and v_gtin_elem.text.startswith('SD'):
                    numeric_gtin = re.sub(r'[^0-9]', '', v_gtin_elem.text)
                    if len(numeric_gtin) >= 13:
                        v_gtin_elem.text = numeric_gtin[:13]
                        fixes_applied['gtin_fixed'] += 1

        # 4. Category'yi düz metin yap (HTML entity olmadan)
        cat_elem = product.find('Category')
        if cat_elem is not None and cat_elem.text:
            # HTML entity'leri decode et
            clean_category = html.unescape(cat_elem.text)
            cat_elem.text = clean_category
            fixes_applied['category_fixed'] += 1

        # 5. MainCategory/SubCategory'yi de düzelt
        for cat_type in ['MainCategory', 'SubCategory']:
            cat_elem = product.find(cat_type)
            if cat_elem is not None and cat_elem.text:
                clean_category = html.unescape(cat_elem.text)
                cat_elem.text = clean_category
                fixes_applied['category_fixed'] += 1

    # XML'i kaydet (UTF-8 encoding ile)
    ET.indent(root, space='  ', level=0)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)

    print("✅ Stokmont XML Format Düzeltmesi Tamamlandı!")
    print("=" * 50)
    print(f"📦 İşlenen ürün sayısı: {product_count}")
    print(f"📝 Temizlenen description: {fixes_applied['description_cleaned']}")
    print(f"🏷️  Düzeltilen GTIN: {fixes_applied['gtin_fixed']}")
    print(f"📂 Düzeltilen kategori: {fixes_applied['category_fixed']}")
    print(f"💾 Çıktı dosyası: {output_file}")

    return fixes_applied

def main():
    input_file = 'stokmont_final_sdstep_titles_buyingprice_barcode_pretty.xml'
    output_file = 'stokmont_final_sdstep_titles_buyingprice_barcode_stokmont.xml'

    try:
        fixes = fix_stokmont_xml(input_file, output_file)
        print(f"\n🎉 Başarılı! {sum(fixes.values())} düzeltme uygulandı.")
        print(f"📄 Yeni dosya: {output_file}")
        print("\n📋 Stokmont'a yüklemek için bu dosyayı kullanın!")
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    main()