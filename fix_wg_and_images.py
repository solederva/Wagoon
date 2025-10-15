#!/usr/bin/env python3
"""
1. Replace all WG- with SD- in ProductCode and VariantCode
2. Add unique query parameters to image URLs to avoid buybox conflicts
"""
import xml.etree.ElementTree as ET
import random
import string

def generate_unique_suffix():
    """Generate a unique 8-character alphanumeric string"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def pretty_write(elem: ET.Element, path: str):
    # Use ET.indent for clean formatting without extra blank lines
    ET.indent(elem, space='  ', level=0)
    tree = ET.ElementTree(elem)
    tree.write(path, encoding='utf-8', xml_declaration=True)

def main():
    in_file = 'stokmont_final_sdstep_titles_buyingprice_barcode_pretty.xml'
    out_file = 'stokmont_final_sdstep_titles_buyingprice_barcode_pretty.xml'
    
    tree = ET.parse(in_file)
    root = tree.getroot()
    
    code_changes = 0
    image_changes = 0
    
    for product in root.findall('.//Product'):
        # 1. Change WG- to SD- in ProductCode
        pc_elem = product.find('ProductCode')
        if pc_elem is not None and pc_elem.text and pc_elem.text.startswith('WG-'):
            pc_elem.text = pc_elem.text.replace('WG-', 'SD-', 1)
            code_changes += 1
        
        # 2. Add unique parameters to image URLs
        unique_param = generate_unique_suffix()
        for i in range(1, 11):  # Image1 to Image10
            img_elem = product.find(f'Image{i}')
            if img_elem is not None and img_elem.text:
                # Add unique query parameter
                separator = '&' if '?' in img_elem.text else '?'
                img_elem.text = f"{img_elem.text}{separator}sd={unique_param}"
                image_changes += 1
        
        # 3. Change WG- to SD- in VariantCode
        variants = product.find('Variants')
        if variants is not None:
            for variant in variants.findall('Variant'):
                vc_elem = variant.find('VariantCode')
                if vc_elem is not None and vc_elem.text and vc_elem.text.startswith('WG-'):
                    vc_elem.text = vc_elem.text.replace('WG-', 'SD-', 1)
                    code_changes += 1
    
    pretty_write(root, out_file)
    print(f"Code changes (WG→SD): {code_changes}")
    print(f"Image URLs updated: {image_changes}")

if __name__ == '__main__':
    main()
