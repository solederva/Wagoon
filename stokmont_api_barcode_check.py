#!/usr/bin/env python3
"""
Stokmont API ile barkod kontrolü yapan script.
Bu script gelecekte barkod çakışmalarını önlemek için kullanılabilir.

NOT: Bu script Stokmont API dokümantasyonu olmadan yazılmıştır.
Gerçek API endpoint'leri ve authentication bilgileri gerekecektir.
"""

import requests
import json
import time
from typing import List, Dict

class StokmontAPI:
    def __init__(self, api_key: str, base_url: str = "https://api.stokmont.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })

    def check_barcode_exists(self, barcode: str) -> bool:
        """
        Stokmont'ta barkodun var olup olmadığını kontrol eder
        """
        try:
            response = self.session.get(f"{self.base_url}/products/check-barcode/{barcode}")
            if response.status_code == 200:
                data = response.json()
                return data.get('exists', False)
            elif response.status_code == 404:
                return False
            else:
                print(f"API hatası: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Bağlantı hatası: {e}")
            return False

    def check_multiple_barcodes(self, barcodes: List[str]) -> Dict[str, bool]:
        """
        Birden fazla barkodu toplu kontrol eder
        """
        results = {}
        for i, barcode in enumerate(barcodes):
            results[barcode] = self.check_barcode_exists(barcode)

            # Rate limiting için bekle
            if i % 10 == 0 and i > 0:
                time.sleep(1)

        return results

    def get_conflicting_barcodes(self, barcodes: List[str]) -> List[str]:
        """
        Çakışan barkodları döndürür
        """
        conflicts = []
        results = self.check_multiple_barcodes(barcodes)

        for barcode, exists in results.items():
            if exists:
                conflicts.append(barcode)

        return conflicts

def main():
    # Örnek kullanım (gerçek API bilgileri gerekli)
    print("⚠️  Bu script Stokmont API dokümantasyonu olmadan yazılmıştır.")
    print("🔧 Gerçek kullanım için API anahtarı ve endpoint bilgileri gereklidir.")
    print("📝 Şu an sadece demo amaçlıdır.")

    # Demo barkodlar
    demo_barcodes = [
        "2525102500015",
        "2525102500022",
        "2525102500039"
    ]

    print(f"📊 Kontrol edilecek barkod sayısı: {len(demo_barcodes)}")
    print("🔍 Demo barkodlar:", demo_barcodes[:3])

    print("\n💡 Gerçek kullanım için:")
    print("1. Stokmont API anahtarınızı alın")
    print("2. API endpoint'lerini öğrenin")
    print("3. Bu script'i güncelleyin")
    print("4. XML yüklemeden önce barkod kontrolü yapın")

if __name__ == "__main__":
    main()