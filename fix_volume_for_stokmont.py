#!/usr/bin/env python3
"""
XML'deki Volume alanını güncelleme scripti.
Stokmont formatına göre Volume = 2 yapılır.
"""

import xml.etree.ElementTree as ET

def update_volume_in_xml(input_file, output_file, volume_value="2"):
    """XML'deki Volume alanını günceller"""

    # XML'i yükle
    tree = ET.parse(input_file)
    root = tree.getroot()

    product_count = 0

    # Her ürün için Volume alanı güncelle
    for product in root.findall('.//Product'):
        product_count += 1

        # Volume elementini bul ve güncelle
        volume_elem = product.find('Volume')
        if volume_elem is not None:
            old_value = volume_elem.text
            volume_elem.text = volume_value

            if product_count <= 3:
                pc = product.findtext('ProductCode', 'N/A')
                print(f"✅ Ürün {pc}: Volume {old_value} → {volume_value}")

    # Desi alanını kaldır (Stokmont formatında yok)
    for product in root.findall('.//Product'):
        desi_elem = product.find('Desi')
        if desi_elem is not None:
            product.remove(desi_elem)
            print("🗑️  Desi alanı kaldırıldı (Stokmont formatında yok)")

    # XML'i kaydet
    ET.indent(root, space='  ', level=0)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)

    print(f"\n✅ {product_count} üründe Volume = {volume_value} yapıldı")
    print(f"💾 Dosya kaydedildi: {output_file}")

def main():
    input_file = 'stokmont_final_sdstep_titles_buyingprice_barcode_pretty.xml'
    output_file = 'stokmont_final_sdstep_titles_buyingprice_barcode_pretty.xml'

    print("🔄 Stokmont Formatına Göre Volume Güncellemesi...")
    print("=" * 50)

    update_volume_in_xml(input_file, output_file, "2")

    print("\n🔍 Doğrulama yapılıyor...")
    # Doğrulama
    tree = ET.parse(output_file)
    root = tree.getroot()

    total_products = len(root.findall('.//Product'))
    products_with_volume_2 = len(root.findall('.//Product[Volume="2"]'))
    products_with_desi = len(root.findall('.//Product[Desi]'))

    print(f"📊 Toplam ürün: {total_products}")
    print(f"✅ Volume=2 olan ürün: {products_with_volume_2}")
    print(f"🗑️  Desi alanı olan ürün: {products_with_desi}")

    if total_products == products_with_volume_2 and products_with_desi == 0:
        print("🎉 Stokmont formatına tam uyumlu!")
    else:
        print("⚠️ Bazı ürünler düzeltilmemiş!")

if __name__ == "__main__":
    main()