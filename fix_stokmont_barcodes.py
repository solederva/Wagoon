#!/usr/bin/env python3
"""
Stokmont için wagoon_source.xml'deki barkodları benzersiz EAN-13 ile değiştir
"""

import xml.etree.ElementTree as ET
from datetime import datetime

class UniqueBarcodeGenerator:
    def __init__(self, store_prefix="25"):  # 25 = Solederva için benzersiz prefix
        self.store_prefix = store_prefix
        self.sequence_counter = 1
        self.used_barcodes = set()

        # Tarih bazlı base prefix (YYMMDD format)
        self.date_prefix = datetime.now().strftime("%y%m%d")

        # Store + Date = ilk 8 karakter
        self.base_prefix = self.store_prefix + self.date_prefix

    def ean13_checksum(self, twelve_digits):
        """EAN-13 checksum hesapla"""
        total = 0
        for i, digit in enumerate(twelve_digits):
            if i % 2 == 0:
                total += int(digit)
            else:
                total += int(digit) * 3
        return str((10 - (total % 10)) % 10)

    def generate_barcode(self):
        """Benzersiz barkod üret"""
        while True:
            # 4 haneli sequence number (0001-9999)
            sequence = f"{self.sequence_counter:04d}"

            # İlk 12 haneli base
            twelve_digit = self.base_prefix + sequence

            # Checksum hesapla
            checksum = self.ean13_checksum(twelve_digit)
            barcode = twelve_digit + checksum

            # Benzersizlik kontrolü
            if barcode not in self.used_barcodes:
                self.used_barcodes.add(barcode)
                self.sequence_counter += 1
                return barcode

            self.sequence_counter += 1

def update_stokmont_xml():
    """wagoon_source.xml'i alıp Stokmont formatında barkodları güncelle"""

    generator = UniqueBarcodeGenerator()

    tree = ET.parse('wagoon_source.xml')
    root = tree.getroot()

    product_count = 0
    variant_count = 0

    print("🔄 Stokmont XML Barkod Güncellemesi")
    print("=" * 50)

    for product in root.findall('.//Product'):
        product_count += 1
        product_code = product.findtext('ProductCode', '')

        # Product Gtin'ini güncelle
        gtin_elem = product.find('Gtin')
        if gtin_elem is not None:
            new_barcode = generator.generate_barcode()
            gtin_elem.text = new_barcode

            if product_count <= 5:
                print(f"Ürün {product_code}: {new_barcode}")

        # Variant Gtin'lerini güncelle
        for variant in product.findall('.//Variant'):
            variant_count += 1

            variant_gtin_elem = variant.find('VariantGtin')
            if variant_gtin_elem is not None:
                new_barcode = generator.generate_barcode()
                variant_gtin_elem.text = new_barcode

    # XML'i kaydet
    ET.indent(root, space='  ', level=0)
    tree.write('stokmont_source_updated.xml', encoding='utf-8', xml_declaration=True)

    print("=" * 50)
    print(f"✅ Başarılı!")
    print(f"📦 Güncellenen ürün sayısı: {product_count}")
    print(f"🏷️ Güncellenen varyant sayısı: {variant_count}")
    print(f"🔢 Toplam yeni barkod: {product_count + variant_count}")
    print(f"💾 Çıktı dosyası: stokmont_source_updated.xml")

if __name__ == "__main__":
    update_stokmont_xml()