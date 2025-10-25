#!/usr/bin/env python3
"""
Güvenli barkod güncelleme scripti - XML yapısını koruyarak sadece barkod değerlerini değiştirir
"""

import xml.etree.ElementTree as ET
import time
import random
from datetime import datetime

class SafeBarcodeGenerator:
    def __init__(self, store_prefix="25"):
        self.store_prefix = store_prefix
        self.sequence_counter = 1
        self.used_barcodes = set()
        
        # Bugünün tarihi (YYMMDD format)
        self.date_prefix = datetime.now().strftime("%y%m%d")
        
        # Store + Date = ilk 8 karakter (25251025)
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
    
    def generate_unique_barcode(self):
        """
        Benzersiz barkod üret: Store(2) + Date(6) + Sequence(4) + Check(1) = 13 digit
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
                print("⚠️  Çok fazla barkod üretildi, prefix değiştiriliyor...")
                self.store_prefix = str(int(self.store_prefix) + 1).zfill(2)
                self.base_prefix = self.store_prefix + self.date_prefix
                self.sequence_counter = 1

def update_barcodes_safely():
    """XML yapısını koruyarak sadece barkod değerlerini günceller"""
    
    input_file = 'stokmont_final_sdstep_titles_buyingprice_barcode_pretty.xml'
    output_file = 'stokmont_final_sdstep_titles_buyingprice_barcode_pretty.xml'
    
    print("🔄 Güvenli Barkod Güncelleme Başlıyor...")
    print("=" * 50)
    
    # XML'i yükle
    tree = ET.parse(input_file)
    root = tree.getroot()
    
    generator = SafeBarcodeGenerator()
    
    product_count = 0
    variant_count = 0
    updated_barcodes = 0
    
    # Önce tüm mevcut barkodları oku
    existing_barcodes = []
    for product in root.findall('.//Product'):
        pb = product.findtext('Barcode')
        if pb: existing_barcodes.append(pb)
        
        for variant in product.findall('.//Variant'):
            vb = variant.findtext('Barcode')
            if vb: existing_barcodes.append(vb)
    
    print(f"📊 Mevcut barkod sayısı: {len(existing_barcodes)}")
    
    # Product barkodlarını güncelle
    for product in root.findall('.//Product'):
        product_count += 1
        
        barcode_elem = product.find('Barcode')
        if barcode_elem is not None and barcode_elem.text:
            new_barcode = generator.generate_unique_barcode()
            barcode_elem.text = new_barcode
            updated_barcodes += 1
            
            if product_count <= 3:
                product_code = product.findtext('ProductCode', 'N/A')
                print(f"✅ Ürün {product_code}: {new_barcode}")
    
    # Variant barkodlarını güncelle  
    for product in root.findall('.//Product'):
        for variant in product.findall('.//Variant'):
            variant_count += 1
            
            barcode_elem = variant.find('Barcode')
            if barcode_elem is not None and barcode_elem.text:
                new_barcode = generator.generate_unique_barcode()
                barcode_elem.text = new_barcode
                updated_barcodes += 1
    
    # XML'i kaydet (pretty format korunur)
    ET.indent(root, space='  ', level=0)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)
    
    print("=" * 50)
    print(f"✅ Güncelleme Tamamlandı!")
    print(f"📦 Ürün sayısı: {product_count}")
    print(f"🏷️  Varyant sayısı: {variant_count}")
    print(f"🔄 Güncellenen barkod: {updated_barcodes}")
    print(f"💾 Dosya: {output_file}")
    
    return updated_barcodes

if __name__ == "__main__":
    try:
        count = update_barcodes_safely()
        print(f"\n🎉 İşlem başarılı! {count} barkod güncellendi.")
    except Exception as e:
        print(f"❌ Hata: {e}")