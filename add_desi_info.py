#!/usr/bin/env python3
"""
XML'e Desi bilgisi ekleme scripti.
Tüm ürünlere Desi = 2 değeri ekler.
"""

import xml.etree.ElementTree as ET

def add_desi_to_xml(input_file, output_file, desi_value="2"):
    """XML'e Desi alanını ekler"""

    # XML'i yükle
    tree = ET.parse(input_file)
    root = tree.getroot()

    product_count = 0

    # Her ürün için Desi alanı ekle
    for product in root.findall('.//Product'):
        product_count += 1

        # Desi elementini kontrol et, yoksa ekle
        desi_elem = product.find('Desi')
        if desi_elem is None:
            # Volume'dan sonra Desi ekle
            volume_elem = product.find('Volume')
            if volume_elem is not None:
                # Volume'dan sonra ekle
                idx = list(product).index(volume_elem)
                desi_elem = ET.Element('Desi')
                desi_elem.text = desi_value
                product.insert(idx + 1, desi_elem)
            else:
                # Volume yoksa Brand'dan önce ekle
                brand_elem = product.find('Brand')
                if brand_elem is not None:
                    idx = list(product).index(brand_elem)
                    desi_elem = ET.Element('Desi')
                    desi_elem.text = desi_value
                    product.insert(idx, desi_elem)
                else:
                    # Hiçbiri yoksa en sona ekle
                    desi_elem = ET.SubElement(product, 'Desi')
                    desi_elem.text = desi_value

        if product_count <= 3:
            pc = product.findtext('ProductCode', 'N/A')
            current_desi = product.findtext('Desi', 'N/A')
            print(f"Ürün {pc}: Desi = {current_desi}")

    # XML'i kaydet
    ET.indent(root, space='  ', level=0)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)

    print(f"\n✅ {product_count} ürüne Desi = {desi_value} eklendi")
    print(f"💾 Dosya kaydedildi: {output_file}")

def main():
    input_file = 'stokmont_final_sdstep_titles_buyingprice_barcode_pretty.xml'
    output_file = 'stokmont_final_sdstep_titles_buyingprice_barcode_pretty.xml'

    print("📦 XML'e Desi Bilgisi Ekleniyor...")
    print("=" * 50)

    add_desi_to_xml(input_file, output_file, "2")

    print("\n🔍 Doğrulama yapılıyor...")
    # Doğrulama
    tree = ET.parse(output_file)
    root = tree.getroot()

    total_products = len(root.findall('.//Product'))
    products_with_desi = len(root.findall('.//Product[Desi]'))

    print(f"📊 Toplam ürün: {total_products}")
    print(f"✅ Desi alanı olan ürün: {products_with_desi}")

    if total_products == products_with_desi:
        print("🎉 Tüm ürünlerde Desi alanı başarıyla eklendi!")
    else:
        print(f"⚠️ {total_products - products_with_desi} üründe Desi alanı eksik!")

if __name__ == "__main__":
    main()