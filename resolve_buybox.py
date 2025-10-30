#!/usr/bin/env python3
"""
Buybox sorununu çözmek için ürün fiyatlarını ve açıklamalarını farklılaştırma scripti
"""
import xml.etree.ElementTree as ET
from datetime import datetime
import random

class BuyboxResolver:
    def __init__(self):
        self.price_variations = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10,
                                0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20,
                                0.21, 0.22, 0.23, 0.24, 0.25, 0.26, 0.27, 0.28, 0.29, 0.30,
                                0.31, 0.32, 0.33, 0.34, 0.35, 0.36, 0.37, 0.38, 0.39, 0.40,
                                0.41, 0.42, 0.43, 0.44, 0.45, 0.46, 0.47, 0.48, 0.49, 0.50]

        self.description_suffixes = [
            " • Kaliteli Ürün",
            " • Orjinal Üretim",
            " • Dayanıklı Malzeme",
            " • Rahat Kullanım",
            " • Şık Tasarım",
            " • Uzun Ömürlü",
            " • Güvenli Kullanım",
            " • Kolay Temizlik",
            " • Hızlı Teslimat",
            " • Müşteri Memnuniyeti",
            " • Profesyonel Hizmet",
            " • Güvenilir Marka",
            " • Kalite Garantisi",
            " • Uygun Fiyat",
            " • En İyi Seçim"
        ]

    def randomize_price(self, base_price):
        """Fiyata küçük bir rastgele fark ekler"""
        variation = random.choice(self.price_variations)
        new_price = float(base_price) + variation
        return ".2f"

    def randomize_description(self, description):
        """Açıklamaya rastgele bir ekleme yapar"""
        if random.choice([True, False]):  # %50 şans
            suffix = random.choice(self.description_suffixes)
            return description + suffix
        return description

    def randomize_brand(self, brand):
        """Brand'e küçük varyasyon ekler"""
        if random.choice([True, False]):  # %50 şans
            return brand + "™"
        return brand

def resolve_buybox_issues(input_file, output_file):
    """Buybox sorunlarını çözmek için XML'i günceller"""

    resolver = BuyboxResolver()

    tree = ET.parse(input_file)
    root = tree.getroot()

    product_count = 0
    price_changes = 0
    desc_changes = 0

    print("🔄 Buybox Sorunlarını Çözme Başladı...")
    print("=" * 60)

    for product in root.findall('.//Product'):
        product_count += 1
        product_code = product.findtext('ProductCode', '')

        # Fiyat değişikliği
        price_elem = product.find('Price')
        if price_elem is not None and price_elem.text:
            old_price = price_elem.text
            new_price = resolver.randomize_price(old_price)
            price_elem.text = new_price
            price_changes += 1
            print(f"💰 {product_code}: {old_price} → {new_price}")

        # Açıklama değişikliği
        desc_elem = product.find('Description')
        if desc_elem is not None and desc_elem.text:
            old_desc = desc_elem.text
            new_desc = resolver.randomize_description(old_desc)
            if new_desc != old_desc:
                desc_elem.text = new_desc
                desc_changes += 1

        # Brand değişikliği
        brand_elem = product.find('Brand')
        if brand_elem is not None and brand_elem.text:
            old_brand = brand_elem.text
            new_brand = resolver.randomize_brand(old_brand)
            if new_brand != old_brand:
                brand_elem.text = new_brand

    # XML'i kaydet
    ET.indent(root, space='  ', level=0)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)

    print("=" * 60)
    print("✅ Buybox Çözümü Tamamlandı!")
    print(f"📦 İşlenen ürün: {product_count}")
    print(f"💰 Fiyat değişikliği: {price_changes}")
    print(f"📝 Açıklama değişikliği: {desc_changes}")
    print(f"💾 Çıktı dosyası: {output_file}")
    print("=" * 60)

if __name__ == "__main__":
    input_file = 'stokmont_final_sdstep_titles_buyingprice_barcode_pretty.xml'
    output_file = 'stokmont_buybox_resolved.xml'

    resolve_buybox_issues(input_file, output_file)