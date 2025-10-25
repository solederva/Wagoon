#!/usr/bin/env python3
"""
Benzersiz ve çakışmayan barkod üretimi için gelişmiş script.
- Tarih/saat bazlı prefix kullanır
- Mağazaya özel prefix ekler  
- Garantili benzersizlik için sequence kullanır
- EAN-13 formatına uygun checksum hesaplar
"""

import xml.etree.ElementTree as ET
import time
import random
import hashlib
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
    
    def generate_barcode(self, product_code="", variant_code=""):
        """
        Benzersiz barkod üret
        Format: [Store:2][Date:6][Sequence:4][Check:1] = 13 digit
        Örnek: 25102501230 + checksum = 251025012304
        """
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
            if self.sequence_counter > 9999:
                # Çok fazla barkod üretildi, prefix değiştir
                self.store_prefix = str(int(self.store_prefix) + 1).zfill(2)
                self.base_prefix = self.store_prefix + self.date_prefix
                self.sequence_counter = 1

    def generate_time_based_barcode(self, product_code=""):
        """
        Zaman bazlı daha da benzersiz barkod
        Format: [Store:2][Unix timestamp son 7 hanesi][Random:3][Check:1]
        """
        while True:
            # Unix timestamp'in son 7 hanesi
            timestamp_part = str(int(time.time()))[-7:]
            
            # 3 haneli random
            random_part = f"{random.randint(0, 999):03d}"
            
            # İlk 12 hane
            twelve_digit = self.store_prefix + timestamp_part + random_part
            
            # Checksum
            checksum = self.ean13_checksum(twelve_digit)
            barcode = twelve_digit + checksum
            
            if barcode not in self.used_barcodes:
                self.used_barcodes.add(barcode)
                return barcode
            
            # Çok nadir çakışma durumunda bekle ve tekrar dene
            time.sleep(0.001)

def update_xml_with_new_barcodes(input_file, output_file, method="sequence"):
    """XML'deki tüm barkodları yeni sistem ile değiştir"""
    
    generator = UniqueBarcodeGenerator()
    
    tree = ET.parse(input_file)
    root = tree.getroot()
    
    product_count = 0
    variant_count = 0
    
    print(f"Barkod üretim metodu: {method}")
    print(f"Store prefix: {generator.store_prefix}")
    print(f"Date prefix: {generator.date_prefix}")
    print("=" * 50)
    
    for product in root.findall('.//Product'):
        product_count += 1
        product_code = product.findtext('ProductCode', '')
        
        # Product barcode'unu güncelle
        product_barcode_elem = product.find('Barcode')
        if product_barcode_elem is not None:
            if method == "time":
                new_barcode = generator.generate_time_based_barcode(product_code)
            else:
                new_barcode = generator.generate_barcode(product_code)
            
            product_barcode_elem.text = new_barcode
            
            if product_count <= 5:
                print(f"Ürün {product_code}: {new_barcode}")
        
        # Variant barcode'larını güncelle
        for variant in product.findall('.//Variant'):
            variant_count += 1
            variant_code = variant.findtext('VariantCode', '')
            
            variant_barcode_elem = variant.find('Barcode')
            if variant_barcode_elem is not None:
                if method == "time":
                    new_barcode = generator.generate_time_based_barcode(variant_code)
                else:
                    new_barcode = generator.generate_barcode(variant_code, variant_code)
                
                variant_barcode_elem.text = new_barcode
    
    # XML'i kaydet
    ET.indent(root, space='  ', level=0)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)
    
    print("=" * 50)
    print(f"✅ Başarılı!")
    print(f"📦 Güncellenen ürün sayısı: {product_count}")
    print(f"🏷️ Güncellenen varyant sayısı: {variant_count}")
    print(f"🔢 Toplam yeni barkod: {product_count + variant_count}")
    print(f"💾 Çıktı dosyası: {output_file}")

def main():
    input_file = 'stokmont_final_sdstep_titles_buyingprice_barcode_pretty.xml'
    output_file = 'stokmont_final_sdstep_titles_buyingprice_barcode_pretty_NEW.xml'
    
    print("🚀 Benzersiz Barkod Üretici")
    print("=" * 50)
    print("1. Sequence-based (önerilen)")
    print("2. Time-based (ultra benzersiz)")
    
    choice = input("Seçiminiz (1/2): ").strip()
    
    if choice == "2":
        update_xml_with_new_barcodes(input_file, output_file, "time")
    else:
        update_xml_with_new_barcodes(input_file, output_file, "sequence")

if __name__ == "__main__":
    main()