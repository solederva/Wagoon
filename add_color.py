import xml.etree.ElementTree as ET

# Kaynak XML'i yükle
source_tree = ET.parse('wagoon_source_pretty.xml')
source_root = source_tree.getroot()

# Hedef XML'i yükle
target_tree = ET.parse('stokmont_final_sdstep_titles_buyingprice_barcode_pretty.xml')
target_root = target_tree.getroot()

# Kaynak ürünlerini dict'e al (ProductCode ile eşleştir)
source_products = {}
for product in source_root.findall('Product'):
    code = product.find('ProductCode').text
    color = product.find('Color')
    if color is not None:
        source_products[code] = color.text

# Hedef ürünlere Color ekle
for product in target_root.findall('Product'):
    code = product.find('ProductCode').text
    # SD- yi WG- ye çevirerek eşleştir
    source_code = code.replace('SD-', 'WG-')
    if source_code in source_products:
        # Color elementini ekle, örneğin Brand'dan sonra
        brand = product.find('Brand')
        if brand is not None:
            color_elem = ET.Element('Color')
            color_elem.text = source_products[source_code]
            brand_index = list(product).index(brand)
            product.insert(brand_index + 1, color_elem)

# Pretty print ile kaydet
ET.indent(target_tree, space="  ", level=0)
target_tree.write('stokmont_final_sdstep_titles_buyingprice_barcode_pretty.xml', encoding='utf-8', xml_declaration=True)

print("Color alanları eklendi.")