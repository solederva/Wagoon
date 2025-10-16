import xml.etree.ElementTree as ET
import random

def ean13_checksum(base):
    """Calculate EAN-13 checksum."""
    total = 0
    for i, digit in enumerate(base):
        if i % 2 == 0:
            total += int(digit) * 1
        else:
            total += int(digit) * 3
    checksum = (10 - (total % 10)) % 10
    return str(checksum)

def generate_random_sd_gtin(existing_gtins):
    """Generate a random SD-prefixed GTIN that's unique."""
    while True:
        # Generate 11 random digits after 'SD'
        random_part = ''.join(random.choice('0123456789') for _ in range(11))
        base = '86' + random_part  # SD is not numeric, but for checksum, use numeric base
        # Actually, since SD is prefix, but GTIN is 13 digits, perhaps make it SD + 11 digits + checksum
        # But to make it EAN-13 like, generate 12 digits, add checksum, prefix SD
        base_12 = ''.join(random.choice('0123456789') for _ in range(12))
        checksum = ean13_checksum(base_12)
        gtin = 'SD' + base_12 + checksum
        if gtin not in existing_gtins:
            existing_gtins.add(gtin)
            return gtin

# XML'i yükle
tree = ET.parse('stokmont_final_sdstep_titles_buyingprice_barcode_pretty.xml')
root = tree.getroot()

existing_gtins = set()

# Ürün GTIN'lerini güncelle
for product in root.findall('Product'):
    gtin_elem = product.find('Gtin')
    if gtin_elem is not None:
        new_gtin = generate_random_sd_gtin(existing_gtins)
        gtin_elem.text = new_gtin

# Varyant GTIN'lerini güncelle
for variant in root.findall('.//Variant'):
    gtin_elem = variant.find('Gtin')
    if gtin_elem is not None:
        new_gtin = generate_random_sd_gtin(existing_gtins)
        gtin_elem.text = new_gtin

# Pretty print ile kaydet
ET.indent(tree, space="  ", level=0)
tree.write('stokmont_final_sdstep_titles_buyingprice_barcode_pretty.xml', encoding='utf-8', xml_declaration=True)

print("GTIN alanları rastgele SD ile başlayan unique değerlere dönüştürüldü.")