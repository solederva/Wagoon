import xml.etree.ElementTree as ET
import random
import string

def is_ean13(barcode):
    return barcode and len(barcode) == 13 and barcode.isdigit()

def generate_barcode(used):
    while True:
        code = ''.join(random.choices('123456789', k=1) + random.choices(string.digits, k=11))
        code += str((10 - (sum((int(x) if i % 2 == 0 else int(x)*3) for i, x in enumerate(code)) % 10)) % 10)
        if code not in used:
            used.add(code)
            return code

def main():
    stokmont_path = 'stokmont_final_sdstep_titles_buyingprice_barcode_pretty.xml'
    wagoon_path = 'wagoon_source_pretty.xml'
    out_path = 'stokmont_final_sdstep_titles_buyingprice_barcode_pretty.xml'
    
    stok_tree = ET.parse(stokmont_path)
    stok_root = stok_tree.getroot()
    wag_tree = ET.parse(wagoon_path)
    wag_root = wag_tree.getroot()
    
    # Map ProductCode -> Variants from kaynak
    wag_map = {}
    for p in wag_root.findall('.//Product'):
        code = p.findtext('ProductCode','').replace('WG-','SD-')
        variants = []
        v_parent = p.find('Variants')
        if v_parent is not None:
            for v in v_parent.findall('Variant'):
                vcode = v.findtext('VariantCode','').replace('WG-','SD-')
                vstock = v.findtext('VariantStock','0')
                vprice = p.findtext('BuyingPrice','0')
                vname = v.findtext('VariantName','')
                vval = v.findtext('VariantValue','')
                variants.append({
                    'VariantCode': vcode,
                    'VariantQuantity': vstock,
                    'VariantPrice': vprice,
                    'VariantName1': vname,
                    'VariantValue1': vval
                })
        wag_map[code] = variants
    # Barkodları topla
    used_barcodes = set()
    for b in stok_root.findall('.//Barcode'):
        if b.text:
            used_barcodes.add(b.text)
    # Eksikleri tamamla
    for product in stok_root.findall('.//Product'):
        code = product.findtext('ProductCode','')
        variants_elem = product.find('Variants')
        if variants_elem is None or not list(variants_elem):
            # Kaynaktan al
            variants = wag_map.get(code,[])
            if not variants:
                # Hiç varyant yoksa, ürünün kendisinden tek varyant oluştur
                price = product.findtext('Price','0')
                variants = [{
                    'VariantCode': code,
                    'VariantQuantity': product.findtext('Quantity','0'),
                    'VariantPrice': price,
                    'VariantName1': '',
                    'VariantValue1': ''
                }]
            # Eskiyi sil
            if variants_elem is not None:
                product.remove(variants_elem)
            # Yeniden ekle
            v_parent = ET.SubElement(product, 'Variants')
            for v in variants:
                v_elem = ET.SubElement(v_parent, 'Variant')
                for k, val in v.items():
                    ET.SubElement(v_elem, k).text = val
                # Barkod
                v_barcode = generate_barcode(used_barcodes)
                ET.SubElement(v_elem, 'Barcode').text = v_barcode
    # Pretty write
    ET.indent(stok_root, space='  ', level=0)
    stok_tree.write(out_path, encoding='utf-8', xml_declaration=True)
    print('Eksik varyantlar tamamlandı ve dosya güncellendi.')

if __name__ == '__main__':
    main()
