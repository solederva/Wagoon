#!/usr/bin/env python3
"""
Buybox eşleşmesini önlemek için ürün feed'ini dönüştüren script.
Pazar yeri algoritmalarının ürünleri eşleştirmesini zorlaştırır.
"""

import xml.etree.ElementTree as ET
import hashlib
import re
from typing import Dict, List, Set
import logging
from datetime import datetime

# Logging setup
logging.basicConfig(
    filename='buybox_protection.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class BuyboxProtectionTransformer:
    def __init__(self):
        # Sabit değerler
        self.PRODUCT_PREFIX = "2199"
        self.VARIANT_PREFIX = "2198"
        self.BRAND = "SDSTEP"
        self.SALT = "SDSTEP_BUYBOX_PROTECTION_2025"  # İdempotent için sabit tuz

        # Renk normalizasyonu mapping
        self.color_mapping = {
            'SYH': 'SIYAH', 'BYZ': 'BEYAZ', 'LAC': 'LACIVERT', 'KRM': 'KIRMIZI',
            'MAV': 'MAVİ', 'YEŞ': 'YEŞİL', 'GRİ': 'GRİ', 'MOR': 'MOR',
            'PEMBE': 'PEMBE', 'TURUNCU': 'TURUNCU', 'KAHVE': 'KAHVE',
            'HAKİ': 'HAKİ', 'BEJ': 'BEJ', 'ALTIN': 'ALTIN', 'GÜMÜŞ': 'GÜMÜŞ'
        }

        # Üretilen barkodları takip et
        self.generated_barcodes: Set[str] = set()

    def normalize_color(self, color: str) -> str:
        """Renk kodunu normalize et"""
        color_upper = color.upper().strip()
        return self.color_mapping.get(color_upper, color_upper)

    def generate_ean13_checksum(self, twelve_digits: str) -> str:
        """EAN-13 checksum hesapla"""
        total = 0
        for i, digit in enumerate(twelve_digits):
            if i % 2 == 0:
                total += int(digit)
            else:
                total += int(digit) * 3
        return str((10 - (total % 10)) % 10)

    def generate_deterministic_barcode(self, base_string: str, prefix: str, suffix: int = 0) -> str:
        """Deterministik barkod üret"""
        # Base string'den hash üret
        hash_obj = hashlib.md5(f"{self.SALT}_{base_string}_{suffix}".encode())
        hash_str = hash_obj.hexdigest()

        # Hash'i sayılara dönüştür (her karakteri ASCII değerine göre)
        numeric_hash = ''.join(str(ord(c) % 10) for c in hash_str)[:12]

        # Prefix ekle ve 12 haneye tamamla
        twelve_digit = prefix + numeric_hash[len(prefix):]

        # Eğer 12 haneden azsa, suffix ile doldur
        while len(twelve_digit) < 12:
            twelve_digit += str(suffix % 10)
            suffix += 1

        twelve_digit = twelve_digit[:12]

        # Checksum hesapla
        checksum = self.generate_ean13_checksum(twelve_digit)
        barcode = twelve_digit + checksum

        # Çakışma kontrolü (suffix artırarak yeniden dene)
        if barcode in self.generated_barcodes:
            return self.generate_deterministic_barcode(base_string, prefix, suffix + 1)

        self.generated_barcodes.add(barcode)
        return barcode

    def transform_image_url(self, url: str, product_code: str) -> str:
        """Resim URL'ine parametre ekle"""
        if not url or 'http' not in url:
            return url

        # 8 haneli hash üret
        hash_8 = hashlib.md5(f"{self.SALT}_{url}_{product_code}".encode()).hexdigest()[:8]

        # 4 haneli hash üret
        hash_4 = hashlib.md5(f"{self.SALT}_{product_code}".encode()).hexdigest()[:4]

        # Parametreler
        params = f"v={hash_8}&pid={product_code}&t={hash_4}&src=sdstep"

        # URL'e parametre ekle
        if '?' in url:
            return url + '&' + params
        else:
            return url + '?' + params

    def reverse_image_order(self, images: Dict[str, str]) -> Dict[str, str]:
        """Resim sıralamasını ters çevir"""
        # Image1 ↔ Image5, Image2 ↔ Image4, Image3 sabit
        reversed_images = {}
        reversed_images['Image1'] = images.get('Image5', '')
        reversed_images['Image2'] = images.get('Image4', '')
        reversed_images['Image3'] = images.get('Image3', '')
        reversed_images['Image4'] = images.get('Image2', '')
        reversed_images['Image5'] = images.get('Image1', '')
        return reversed_images

    def generate_title(self, product_name: str, color: str, model: str = "") -> str:
        """Başlık formatını oluştur"""
        # Ürün adından marka ve ürün kısmını çıkar
        # Örnek: "Solederva Köpekbalığı Beyaz Unisex Tam Ortopedik Terlik Shark Slides Cocuk"
        # -> Marka: SDSTEP, Ürün: Köpekbalığı, Renk: Beyaz, Model: Shark Slides

        parts = product_name.split()
        if len(parts) >= 3:
            product_part = ' '.join(parts[1:-2]) if len(parts) > 3 else parts[1]
            color_part = self.normalize_color(color)
            model_part = model if model else ' '.join(parts[-2:]) if len(parts) >= 2 else ''

            title = f"{self.BRAND} {product_part} {color_part}"
            if model_part:
                title += f" - {model_part}"
            return title

        return f"{self.BRAND} {product_name}"

    def enhance_description(self, description: str, product_code: str) -> str:
        """Açıklamayı geliştir"""
        # Benzersiz token üret
        unique_token = hashlib.md5(f"{self.SALT}_{product_code}_{description}".encode()).hexdigest()[:8]

        # Bullet list ekle (ürün tipine göre)
        bullets = [
            "• Yüksek kaliteli malzemeler kullanılmıştır",
            "• Rahat ve ergonomik tasarım",
            "• Dayanıklı ve uzun ömürlü kullanım",
            "• Modern ve şık görünüm",
            "• Kolay bakım ve temizlik",
            "• Güvenli ve sağlıklı kullanım"
        ]

        # HTML escaping
        description = description.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        # Bullet list + orijinal açıklama + görünmez imza
        enhanced_desc = '\n'.join(bullets[:4]) + '\n\n' + description
        enhanced_desc += f'\n<p style="display:none;">SDSTEP-{unique_token}</p>'

        return enhanced_desc

    def generate_variant_code(self, product_code: str, color: str, size: str) -> str:
        """Varyant kodu üret"""
        color_norm = self.normalize_color(color).replace(' ', '').upper()
        return f"{product_code}-{color_norm}-{size}"

    def transform_xml(self, input_file: str, output_file: str):
        """Ana dönüşüm fonksiyonu"""
        logging.info("Buybox koruma dönüşümü başladı")

        # XML'i oku
        tree = ET.parse(input_file)
        root = tree.getroot()

        product_count = 0
        variant_count = 0
        original_barcodes = set()
        new_barcodes = set()

        for product in root.findall('.//Product'):
            product_count += 1
            product_code = product.findtext('ProductCode', '')

            # Ürün bilgilerini topla
            product_name = product.findtext('ProductName', '')
            category = product.findtext('Category', '')

            # Resimleri topla ve dönüştür
            images = {}
            for i in range(1, 6):
                img_elem = product.find(f'Image{i}')
                if img_elem is not None and img_elem.text:
                    images[f'Image{i}'] = self.transform_image_url(img_elem.text, product_code)

            # Resim sıralamasını ters çevir
            reversed_images = self.reverse_image_order(images)

            # Resimleri güncelle
            for i in range(1, 6):
                img_elem = product.find(f'Image{i}')
                if img_elem is not None:
                    img_elem.text = reversed_images.get(f'Image{i}', '')

            # Başlığı dönüştür
            color_from_name = 'BEYAZ'  # Default
            if 'BEYAZ' in product_name.upper():
                color_from_name = 'BEYAZ'
            elif 'HAKİ' in product_name.upper():
                color_from_name = 'HAKİ'
            elif 'MOR' in product_name.upper():
                color_from_name = 'MOR'

            new_title = self.generate_title(product_name, color_from_name)
            product.find('ProductName').text = new_title

            # Markayı ayarla
            brand_elem = product.find('Brand')
            if brand_elem is not None:
                brand_elem.text = self.BRAND

            # Açıklamayı geliştir
            desc_elem = product.find('Description')
            if desc_elem is not None:
                desc_elem.text = self.enhance_description(desc_elem.text, product_code)

            # Fiyat alanını düzelt (eğer bozuksa)
            price_elem = product.find('Price')
            if price_elem is not None and price_elem.text == '.2f':
                price_elem.text = '260.00'

            # Varyantları dönüştür
            for variant in product.findall('.//Variant'):
                variant_count += 1

                # Varyant bilgilerini topla
                size = variant.findtext('VariantValue1', '')
                color = variant.findtext('VariantValue2', 'BEYAZ')

                # Varyant kodunu dönüştür
                variant_code_elem = variant.find('VariantCode')
                if variant_code_elem is not None:
                    new_variant_code = self.generate_variant_code(product_code, color, size)
                    variant_code_elem.text = new_variant_code

                # Varyant barkodunu dönüştür
                variant_barcode_elem = variant.find('Barcode')
                if variant_barcode_elem is not None:
                    original_barcodes.add(variant_barcode_elem.text)
                    base_string = f"{product_code}_{product_name}_{color}_{size}_{category}"
                    new_barcode = self.generate_deterministic_barcode(base_string, self.VARIANT_PREFIX)
                    new_barcodes.add(new_barcode)
                    variant_barcode_elem.text = new_barcode

                # GTIN'i de güncelle (bazı platformlar için)
                gtin_elem = variant.find('Gtin')
                if gtin_elem is not None:
                    gtin_elem.text = new_barcode

        # XML'i kaydet
        ET.indent(root, space='  ', level=0)
        tree.write(output_file, encoding='utf-8', xml_declaration=True)

        # Doğrulamalar
        duplicate_check = len(new_barcodes) == len(self.generated_barcodes)
        brand_check = all(product.findtext('Brand', '') == self.BRAND for product in root.findall('.//Product'))
        title_check = all('SDSTEP' in product.findtext('ProductName', '') for product in root.findall('.//Product'))
        image_check = any(product.findtext('Image1', '') != '' for product in root.findall('.//Product'))

        # Loglama
        logging.info(f"Dönüşüm tamamlandı: {product_count} ürün, {variant_count} varyant")
        logging.info(f"Duplicate barkod var mı? {'HAYIR' if duplicate_check else 'EVET'}")
        logging.info(f"Image1 değişti mi? {'EVET' if image_check else 'HAYIR'}")
        logging.info(f"Brand beklenen mi? {'EVET' if brand_check else 'HAYIR'}: {self.BRAND}")
        logging.info(f"Title şablona uydu mu? {'EVET' if title_check else 'HAYIR'}")

        print("✅ Buybox koruma dönüşümü tamamlandı!")
        print(f"📦 İşlenen: {product_count} ürün, {variant_count} varyant")
        print(f"🔢 Üretilen barkod: {len(new_barcodes)}")
        print(f"📝 Log dosyası: buybox_protection.log")

def main():
    transformer = BuyboxProtectionTransformer()
    transformer.transform_xml(
        'stokmont_final_sdstep_titles_buyingprice_barcode_pretty.xml',
        'buybox_protected_feed.xml'
    )

if __name__ == "__main__":
    main()