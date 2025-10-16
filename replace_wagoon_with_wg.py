import xml.etree.ElementTree as ET

# XML'i yükle
tree = ET.parse('stokmont_final_sdstep_titles_buyingprice_barcode_pretty.xml')
root = tree.getroot()

# Tüm elementlerde text değiştir
def replace_text(element):
    if element.text:
        element.text = element.text.replace('Wagoon', 'WG')
    if element.tail:
        element.tail = element.tail.replace('Wagoon', 'WG')
    for child in element:
        replace_text(child)

replace_text(root)

# Pretty print ile kaydet
ET.indent(tree, space="  ", level=0)
tree.write('stokmont_final_sdstep_titles_buyingprice_barcode_pretty.xml', encoding='utf-8', xml_declaration=True)

print("Tüm 'Wagoon' kelimeleri 'WG' ile değiştirildi.")