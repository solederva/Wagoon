import xml.etree.ElementTree as ET

# Kaynak XML'den renkleri al
source_tree = ET.parse('wagoon_source_pretty.xml')
source_root = source_tree.getroot()

# ProductCode -> Color eşlemesi
product_colors = {}
for product in source_root.findall('Product'):
    code = product.find('ProductCode').text
    color = product.find('Color')
    if color is not None:
        product_colors[code] = color.text

# Hedef XML'i yükle
target_tree = ET.parse('stokmont_final_sdstep_titles_buyingprice_barcode_pretty.xml')
target_root = target_tree.getroot()

for product in target_root.findall('Product'):
    code = product.find('ProductCode').text
    # SD- yi WG- ye çevirerek eşleştir
    source_code = code.replace('SD-', 'WG-')
    color = product_colors.get(source_code, None)
    if color:
        # Varyantlara renk ekle
        for variant in product.find('Variants').findall('Variant'):
            # Eğer zaten renk varyantı varsa ekleme
            if not any((vn.text or '').lower() == 'renk' for vn in variant.findall('*') if vn.tag.startswith('VariantName')):
                # İlk boş VariantName/Value slotunu bul
                for i in range(1, 6):
                    if variant.find(f'VariantName{i}') is None:
                        ET.SubElement(variant, f'VariantName{i}').text = 'Renk'
                        ET.SubElement(variant, f'VariantValue{i}').text = color
                        break
        # Ana üründeki Color alanını kaldır
        color_elem = product.find('Color')
        if color_elem is not None:
            product.remove(color_elem)

# Pretty print ile kaydet
ET.indent(target_tree, space="  ", level=0)
target_tree.write('stokmont_final_sdstep_titles_buyingprice_barcode_pretty.xml', encoding='utf-8', xml_declaration=True)

print("Renk bilgisi varyantlara taşındı, ana üründen kaldırıldı.")