import os
import xml.etree.ElementTree as ET

value_KEYTERM   = "XML_VALUE132"
UNKNOWN_DATATYPE= "UNKNOWN_DATATYPE"

def build_XML

def XML_key():
    return value_KEYTERM

def XML_is_leaf(element):
    temp = etree_to_dict(element)
    is_leaf = False
    if len(temp[element.tag]) == 0 and not element.attrib:
        is_leaf = True
    return is_leaf

def XML_list_nodes(element):
    out_list = []
    for item in element:
        out_list.append(item.iter())
    return out_list
    
def XML_load_file(file_path):
    if not os.path.exists(file_path):
        print("File not found %s"%(file_path))
        return None
    data = ET.parse(file_path)
    TEMP = etree_to_dict(data.getroot())
    #print(TEMP)
    return data.getroot()
    
def XML_get_attributes(data):
    return data.attrib  
def XML_get_data(data):
    return data.findall("./")
def XML_get_tag(data):
    return data.tag
def XML_get_leaf_data(data):
    return [data.tag,data.text]
def XML_data_type(data):
    data_type = type("")
    if data is None:
        data_type = type(None)
    elif is_float(data):
        data_type = type(1.2)
    elif is_int(data):
        data_type = type(1)
    return data_type
        
def is_float(data):
    try:
        float(data)
        if "." in data:
            return True
    except:
        pass
    return False
def is_int(data):
    try:
        int(data)
        return True
    except:
        pass
    return False
def etree_to_dict(t):
    d = {t.tag : map(etree_to_dict, t.getchildren())}
    d.update(('@' + k, v) for k, v in t.attrib.iteritems())
    d[value_KEYTERM] = t.text
    return d