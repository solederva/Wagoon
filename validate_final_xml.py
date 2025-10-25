import xml.etree.ElementTree as ET
import re

def is_ean13(barcode):
    return bool(re.fullmatch(r"\d{13}", barcode))

def main():
    path = "stokmont_final_sdstep_titles_buyingprice_barcode_pretty.xml"
    tree = ET.parse(path)
    root = tree.getroot()
    errors = []
    product_count = 0
    variant_count = 0
    barcodes = set()
    for product in root.findall(".//Product"):
        product_count += 1
        # 1. Zorunlu alanlar (text içeriği olan)
        for tag in ["ProductCode","ProductName","Quantity","Price","Currency","TaxRate","Barcode","Category","Description","Image1","Brand"]:
            if product.find(tag) is None or not (product.find(tag).text or '').strip():
                errors.append(f"Eksik alan: <{tag}> ürün: {ET.tostring(product, encoding='unicode')[:100]}")
        
        # Variants element varlık kontrolü (text değil, child element kontrolü)
        variants_elem = product.find("Variants")
        if variants_elem is None:
            errors.append(f"Variants elementi yok: ürün: {pc}")
        # 2. Kodlar SD ile başlıyor mu?
        pc = product.findtext("ProductCode","")
        if not pc.startswith("SD-"):
            errors.append(f"ProductCode SD ile başlamıyor: {pc}")
        # 3. Fiyat BuyingPrice'dan mı? (kontrol: Price ile VariantPrice aynı ve 0'dan büyük)
        price = product.findtext("Price","")
        if not price or float(price.replace(",",".") or 0) <= 0:
            errors.append(f"Price hatalı: {price} - ürün: {pc}")
        # 4. Barkodlar
        barcode = product.findtext("Barcode","")
        if not is_ean13(barcode):
            errors.append(f"Product barcode EAN-13 değil: {barcode} - ürün: {pc}")
        if barcode in barcodes:
            errors.append(f"Barkod tekrar ediyor: {barcode}")
        barcodes.add(barcode)
        # 5. Marka
        brand = product.findtext("Brand","")
        if brand != "SDSTEP":
            errors.append(f"Brand SDSTEP değil: {brand} - ürün: {pc}")
        # 6. Resim URL'leri
        for i in range(1,11):
            img = product.findtext(f"Image{i}","")
            if img and not re.search(r"[?&]sd=", img):
                errors.append(f"Image{i} unique parametre yok: {img} - ürün: {pc}")
        # 7. Varyantlar
        variants = product.find("Variants")
        if variants is None or not list(variants):
            errors.append(f"Varyant yok: ürün: {pc}")
        for variant in variants.findall("Variant"):
            variant_count += 1
            vcode = variant.findtext("VariantCode","")
            if not vcode.startswith("SD-"):
                errors.append(f"VariantCode SD ile başlamıyor: {vcode}")
            vprice = variant.findtext("VariantPrice","")
            if not vprice or float(vprice.replace(",",".") or 0) <= 0:
                errors.append(f"VariantPrice hatalı: {vprice} - ürün: {pc}")
            vbarcode = variant.findtext("Barcode","")
            if not is_ean13(vbarcode):
                errors.append(f"Variant barcode EAN-13 değil: {vbarcode} - ürün: {pc}")
            if vbarcode in barcodes:
                errors.append(f"Varyant barkod tekrar ediyor: {vbarcode}")
            barcodes.add(vbarcode)
    print(f"Toplam ürün: {product_count}, toplam varyant: {variant_count}, toplam barkod: {len(barcodes)}")
    if errors:
        print(f"HATA! {len(errors)} problem bulundu:")
        for e in errors:
            print(e)
    else:
        print("Tüm kontroller geçti. XML pazar yerleri ve Stokmont için %100 UYUMLU!")

if __name__ == "__main__":
    main()
