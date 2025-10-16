import xml.etree.ElementTree as ET
import re

# Renk eşleme tablosu (özel renkler için)
renk_map = {
    'kömür': 'Siyah',
    'siyah siyah': 'Siyah',
    'siyah 2': 'Siyah',
    'siyah 5': 'Siyah',
    'beyaz 1': 'Beyaz',
    'beyaz 2': 'Beyaz',
    'beyaz': 'Beyaz',
    'siyah': 'Siyah',
    'gri': 'Gri',
    'mor': 'Mor',
    'haki': 'Haki',
    'lacivert': 'Lacivert',
    'kırmızı': 'Kırmızı',
    'sarı': 'Sarı',
    'pembe': 'Pembe',
}

def normalize_renk(renk):
    if not renk:
        return ''
    renk = renk.strip().lower()
    # Sayı ve ekleri sil
    renk = re.sub(r'\s*\d+$', '', renk)
    renk = re.sub(r'\s*\d+\s*', ' ', renk)
    renk = renk.replace('  ', ' ')
    # Eşleme tablosu ile düzelt
    if renk in renk_map:
        return renk_map[renk]
    # İlk harf büyük, diğerleri küçük
    return renk.capitalize()

# Kaynak XML'i yükle
source_tree = ET.parse('wagoon_source_pretty.xml')
source_root = source_tree.getroot()

# ProductCode -> Normalized Color eşlemesi
product_colors = {}
for product in source_root.findall('Product'):
    code = product.find('ProductCode').text
    color = product.find('Color')
    if color is not None:
        product_colors[code] = normalize_renk(color.text)

# Hedef XML'i yükle
target_tree = ET.parse('stokmont_final_sdstep_titles_buyingprice_barcode_pretty.xml')
target_root = target_tree.getroot()

for product in target_root.findall('Product'):
    code = product.find('ProductCode').text
    source_code = code.replace('SD-', 'WG-')
    color = product_colors.get(source_code, None)
    if color:
        for variant in product.find('Variants').findall('Variant'):
            # Renk varyantı varsa güncelle, yoksa ekle
            renk_var = False
            for i in range(1, 6):
                vn = variant.find(f'VariantName{i}')
                vv = variant.find(f'VariantValue{i}')
                if vn is not None and (vn.text or '').lower() == 'renk':
                    renk_var = True
                    if vv is not None:
                        vv.text = color
            if not renk_var:
                # İlk boş slotu bul
                for i in range(1, 6):
                    if variant.find(f'VariantName{i}') is None:
                        ET.SubElement(variant, f'VariantName{i}').text = 'Renk'
                        ET.SubElement(variant, f'VariantValue{i}').text = color
                        break

# Pretty print ile kaydet
ET.indent(target_tree, space="  ", level=0)
target_tree.write('stokmont_final_sdstep_titles_buyingprice_barcode_pretty.xml', encoding='utf-8', xml_declaration=True)

print("Renkler normalize edildi ve varyantlara uygulandı.")
