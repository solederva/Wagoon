from xml.dom import minidom

def remove_empty_lines(xml_string):
    lines = xml_string.decode('utf-8').split('\n')
    cleaned_lines = [line for line in lines if line.strip()]
    return '\n'.join(cleaned_lines).encode('utf-8')

with open('stokmont_final.xml', 'r', encoding='utf-8') as f:
    xml = f.read()

dom = minidom.parseString(xml)
pretty = dom.toprettyxml(indent='  ', encoding='utf-8')

# Fazla boş satırları temizle
pretty_cleaned = remove_empty_lines(pretty)

with open('stokmont_final_pretty.xml', 'wb') as f:
    f.write(pretty_cleaned)

print('Pretty XML yazıldı: stokmont_final_pretty.xml')
