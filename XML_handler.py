import os
#import xml.etree.ElementTree as ET
from lxml import etree as ET
from copy import deepcopy
value_KEYTERM   = "XML_VALUE132"
UNKNOWN_DATATYPE= "UNKNOWN_DATATYPE"

HEADER = ""
def generate_XML_file(data,file_path):
    if not type(data) == type(""):
        data = ET.tostring(data,pretty_print=True)
    file = open(file_path, "w")
    file.write(HEADER)
    file.write(data)
    file.close()

def read_value(XML_file_path,data_path):
    if type(XML_file_path) == type(""):
        data = ET.parse(XML_file_path)
        root = data.getroot()
    elif isinstance(XML_file_path,ET._Element):
        root = XML_file_path
    else:
        root = XML_file_path.getroot()
    val = root.find(data_path).text
    return val

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
    global HEADER
    if not os.path.exists(file_path):
        print("File not found %s"%(file_path))
        return None
    data = ET.parse(file_path)
    TEMP = etree_to_dict(data.getroot())
    #print(TEMP)
    
    file = open(file_path)
    temp = file.readline()
    if("xml version" in temp):
        HEADER = temp
    else:
        HEADER = ""
    file.close()
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
    
    
    
#Oh god I am sorry, please never look at this code
#If you do, please don't judge me    
def is_bottom(data):
    is_bot = True
    if len(data) > 0:
        if not type(data[0]) == type(""):
            is_bot = False
    return is_bot
def traverse_data(data,traversal):
    temp = data
    #print(data)
    #print(traversal)
    for trav in traversal:
        temp = temp[trav]
    return temp
def create_data_lists(data,cur_list,traversal=[]):
    if is_bottom(data):
        num_items = len(data)
        #For each different value (except first), create copy of each preceeding XML_VALUE132
        #Now with updated value
        list_len = len(cur_list)
        for i in range(1,num_items):
            for j in range(list_len):
                
                cur_copy = deepcopy(cur_list[j])
                #print(traversal)
                #print("END")
                cur_tree = traverse_data(cur_copy,traversal)
                cur_tree[0] = data[i]
                cur_list.append(deepcopy(cur_copy))
    else:
        for id,item in enumerate(data):
            trav_t = deepcopy(traversal)
            trav_t.append(id)
            create_data_lists(item,cur_list,trav_t)
    
    return cur_list
def create_initial_list(data,list=[],traversal=[]):

    cur_val = traverse_data(list,traversal)
    if is_bottom(data) and len(data) > 0:
        cur_val.append([])
        cur_val[0] = deepcopy(data[0])
    else:
        for id,item in enumerate(data):
            trav_t = deepcopy(traversal)
            trav_t.append(id)
            cur_val.append([])
            create_initial_list(item,list,trav_t)
    return list

def construct_XML(tags,attributes,data,root_node=None):
    sub_tags = deepcopy(tags)
    sub_attributes = deepcopy(attributes)
    del sub_tags[0]
    del sub_attributes[0]
    cur_tag = tags[0]
    cur_attributes = attributes[0]
    
    new_node = ET.Element(cur_tag)
    if root_node is None:
        root_node = ET.ElementTree(new_node)
    else:
        root_node.append(new_node)
    for value in cur_attributes:
        str_arr = value.split("====")
        key = str_arr[0]
        val = str_arr[1]
        new_node.set(key,val)
        
    for id,(cur_tag,cur_attributes,cur_data) in enumerate(zip(sub_tags,sub_attributes,data)):
        if isinstance(cur_tag,list):
            construct_XML(cur_tag,cur_attributes,cur_data,new_node)
        else:
            temp_node = ET.Element(cur_tag)
            for value in cur_attributes:
                str_arr = value.split("====")
                key = str_arr[0]
                val = str_arr[1]
                temp_node.set(key,val)
            temp_node.text = cur_data[0]
            new_node.append(deepcopy(temp_node))
    #This block sets the current attributes
        
    return root_node
def XML_struct_to_str(XML_data):
    return HEADER + ET.tostring(XML_data,pretty_print=True)
def build_XML(tags,attributes,data_in,profile_prefix_name):
    global HEADER
    print("Generating data hypercube")
    XML_list = []
    data = deepcopy(data_in)
    #print("DATA")
    #print(data)
    first_list = create_initial_list(data,[],[])
    #print("data_again")
    #print(data)
    data_list = create_data_lists(data,[first_list])
    
    print("Generating XML strings")
    attributes[0].insert(0,"")
    for id,cur_data in enumerate(data_list):
        #Assembles the current XML object
        cur_profile_name = str("%s_%d"%(profile_prefix_name,id)) 
        attributes[0][0] = str("name====%s"%(cur_profile_name))
        cur_XML = construct_XML(tags,attributes,cur_data)
        
        #Converts to string to be stored by other process
        XML_list.append(cur_XML)
    
    return XML_list