import xml.etree.ElementTree as ET

def pretty_write(elem: ET.Element, path: str):
    ET.indent(elem, space='  ', level=0)
    tree = ET.ElementTree(elem)
    tree.write(path, encoding='utf-8', xml_declaration=True)

def main():
    in_file = 'wagoon_source.xml'
    out_file = 'wagoon_source_pretty.xml'
    tree = ET.parse(in_file)
    root = tree.getroot()
    pretty_write(root, out_file)
    print(f"Pretty XML yazıldı: {out_file}")

if __name__ == '__main__':
    main()
