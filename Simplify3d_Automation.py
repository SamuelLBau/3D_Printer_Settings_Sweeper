import pyautogui
import numpy as np
import struct
import stl
import time
from math import ceil
import os
import shutil
import tkMessageBox

#Used to copy model and generate XL file
from shutil import copyfile
import xlsxwriter

from XML_handler import read_value,generate_XML_file

ABS_DIR = os.path.dirname(os.path.realpath(__file__))

SRC_DIR = ABS_DIR + "/src/"
SAMPLE_IMAGE_DIR = SRC_DIR + "Simplify_images/"
FACTORY_DIR = SRC_DIR + "factory_files/"
PRINT_BED_EDGE = 10
PRINT_MIN_DISTANCE = 5              #After object size and printer head accounted for, what minimum spacing between print head and other objects
PRINTER_HEAD_SIZE = [25,25,25,25]   #[neg_x,pos_x,neg_y,pos_y] #Distance from printer nozzel to protruding ends of print head

TYPE_DELAY = .01
TAB_DELAY = .1
WINDOW_DELAY = .2
NUM_IMAGE_SEARCH_TRIES = 1

BUTTON_LOCATIONS = {}

def open_Simplify3D():
    tkMessageBox.askokcancel("Open Simplify","Please open Simplify3D")
    time.sleep(2)
    BUTTON_LOCATIONS = {}
    pass
def close_Simplify3D():
    BUTTON_LOCATIONS = {}

def add_model(model_file):
    pass

def locate_button_center(file_name,bypass=True,max_num_tries=NUM_IMAGE_SEARCH_TRIES):
    global BUTTON_LOCATIONS
    cur_tries = 0
    if (not file_name in BUTTON_LOCATIONS) or not bypass:
        while cur_tries < max_num_tries:
            try:
                time.sleep(WINDOW_DELAY)
                loc = pyautogui.locateOnScreen(SAMPLE_IMAGE_DIR + file_name)
                center = [loc[0] + loc[2] / 2, loc[1] + loc[3] / 2]
                BUTTON_LOCATIONS[file_name] = center
                break
            except:
                print("COULD NOT FIND IMAGE, moving mouse and trying again in .5 seconds")
                pyautogui.moveRel(100,100)
                time.sleep(.5)
            cur_tries += 1
        else:
            raise Exception("Failed to find image %s on screen, quitting now"%(file_name))
    return BUTTON_LOCATIONS[file_name]

def repeat_press(button,iter,delay=TAB_DELAY):
    pyautogui.typewrite([button]*iter,interval=delay)

def new_factory():
    pyautogui.hotkey("ctrl", "n")
    pyautogui.typewrite(["right", "enter"])


def save_factory(factory_path):
    pyautogui.hotkey("ctrl","s")
    time.sleep(WINDOW_DELAY)
    type_path(factory_path)
    pyautogui.typewrite(["enter"])
    time.sleep(WINDOW_DELAY)


def clear_settings(settings):
    num_settings=len(settings)
    import_new_setting(settings[0])

    loc = locate_button_center("add_process_button.png")
    pyautogui.click(loc[0],loc[1],clicks=1)
    repeat_press(["tab"],4)
    pyautogui.typewrite(["enter"])
    pyautogui.typewrite(["tab"])
    repeat_press("enter",2)
    time.sleep(WINDOW_DELAY)
    repeat_press(["tab"],6)
    pyautogui.typewrite(["enter"])
    loc = locate_button_center("delete_process_button.png")
    pyautogui.click(loc[0],loc[1],clicks=num_settings+2)

def import_new_setting(file_path):
    cen = locate_button_center("file_button.png")
    pyautogui.click(x=cen[0],y=cen[1],clicks=1)

    repeat_press("down",6,TAB_DELAY)
    pyautogui.typewrite(["enter"])
    print(file_path)
    type_path(file_path)

    repeat_press("enter", 2)

def type_path(file_path):
    file_path = file_path.replace("/","\\")
    pyautogui.typewrite(file_path, TYPE_DELAY)

def new_model(model_path,pos,model_name="temp"):
    pyautogui.hotkey('ctrl', 'i')
    type_path(model_path)
    pyautogui.typewrite(["enter"])
    try:
        loc = locate_button_center("cur_model_color.png",bypass=False)
    except:
        loc = locate_button_center("cur_model_color2.png", bypass=False)
    pyautogui.click(loc[0],loc[1],clicks=2)
    repeat_press("tab", 10,TAB_DELAY)
    pyautogui.typewrite(model_name)
    repeat_press("tab", 1)
    pyautogui.typewrite(str(pos[0]))
    repeat_press("tab", 1)
    pyautogui.typewrite(str(pos[1]))

def process_select_model(settings_num):
    print("SELECTING MODEL")
    loc = locate_button_center("select_models_button.png")
    pyautogui.click(loc[0], loc[1], clicks=1)
    time.sleep(WINDOW_DELAY)
    loc = locate_button_center("select_none_button.png")
    pyautogui.click(loc[0], loc[1], clicks=1)
    repeat_press(["down"], settings_num)
    time.sleep(.1)
    #repeat_press(["tab"],2+settings_num)
    #pyautogui.typewrite(["enter"])          #Select None
    loc = locate_button_center("process_select_model_empty.png",bypass=False)
    pyautogui.click(loc[0],loc[1],clicks=1)
    time.sleep(WINDOW_DELAY)
    repeat_press(["tab"],3,TAB_DELAY)
    pyautogui.typewrite(["enter"])          #Select close select model screen
    time.sleep(WINDOW_DELAY)

def add_process(settings_num,process_name):
    loc = locate_button_center("add_process_button.png")
    pyautogui.click(loc[0], loc[1], clicks=1)
    time.sleep(WINDOW_DELAY)
    pyautogui.typewrite(["tab"])
    loc = locate_button_center("process_drop_down.png")
    pyautogui.click(loc[0], loc[1], clicks=1)
    time.sleep(WINDOW_DELAY)
    pyautogui.typewrite(["down"])
    pyautogui.typewrite(["enter"])
    pyautogui.hotkey("shift","tab")
    repeat_press(["backspace"],10,TYPE_DELAY)
    pyautogui.typewrite(process_name)
    pyautogui.typewrite(["tab"])
    process_select_model(settings_num)
    pyautogui.typewrite(["tab"])
    pyautogui.typewrite(["enter"])


def generate_factory(settings,pos_list,model,factory_path,offset=0):

    print("GENERATING FARCTORY")

    new_factory()
    clear_settings(settings)

    for id in range(len(settings)):
        model_name = str("model_%d"%(id+offset))
        new_model(model,pos_list[id],model_name)

    for id,cur_set in enumerate(settings):
        process_name = str("model_%d_process" % (id+offset))
        import_new_setting(cur_set)
        add_process(id,process_name)
    print("SAVING FACTORY")
    save_factory(factory_path)

def generate_factories(XML_data,model,prefix,distance_params={}):
    pos_list = arrange_models(XML_data[0], model,distance_params=distance_params)
    items_per_factory = pos_list.shape[0]
    num_objects = len(XML_data)
    num_factories = int(ceil( float(num_objects) / float(len(pos_list))))


    objects_written = 0
    base_folder = FACTORY_DIR+prefix
    if os.path.isdir(base_folder):
        shutil.rmtree(base_folder, ignore_errors=True)
    os.mkdir(base_folder)
    base_folder = base_folder + "/"
    
    print(model)
    #Place model in base folder
    model_name = model.split("/")[-1]
    model_path = base_folder + model_name
    print(model_path)
    copyfile(model,model_path.replace("\\","/"))
    model = model_path
    
    #Place empty excel sheet in base folder
    excel_path = base_folder + prefix + "_grading.xlsx"
    #copyfile("./src/empty_excel.xlsx",excel_path.replace("\\","/"))
    workbook = xlsxwriter.Workbook(excel_path)
    worksheet = workbook.add_worksheet()
    worksheet.write(0,0,model_name)
    worksheet.write(1,0,"Settings file")
    worksheet.write(1,1,"Grades")
    
    offset_count = 1
    for i in range(0,len(XML_data)):
        setting_name_str = str("%s_%d.fff"%(prefix,i))
        if i%items_per_factory == 0:
            worksheet.write(i+offset_count,0,str("Print job %d"%(int(i/items_per_factory))))
            worksheet.write(i+offset_count,1,"Grades")
            offset_count += 1
        worksheet.write(i+offset_count,0,setting_name_str)
    workbook.close()
    
    
    
    open_Simplify3D()
    for fac_num in range(num_factories):
        cur_fac_dir = base_folder + str("%s%d"%("Print_job_",fac_num))
        settings_dir = cur_fac_dir+"/settings"
        os.mkdir(cur_fac_dir)
        os.mkdir(settings_dir)
        factory_path = str("%s/%s_%d.factory"%(cur_fac_dir,prefix,fac_num))
        cur_settings = []
        for i in range(items_per_factory):
            if objects_written >= num_objects:
                break
            settings_file = str("%s/%s_%d.fff"%(settings_dir,prefix,objects_written))
            generate_XML_file(XML_data[objects_written],settings_file)
            cur_settings.append(settings_file)
            objects_written += 1

        model_num_offset = fac_num*items_per_factory
        generate_factory(cur_settings,pos_list,model,factory_path,offset=model_num_offset)
        time.sleep(2)#Give program time to save

    close_Simplify3D()
    
    
def load_default_distance_params():
    global PRINTER_HEAD_SIZE
    global PRINT_BED_EDGE
    global PRINT_MIN_DISTANCE

    file = open("./src/printer_information.txt")
    for line in file:
        line_split = line.split(",")
        if line_split[0] == "PRINTER_HEAD_SIZE":
            PRINTER_HEAD_SIZE = line_split[1:]
            for i in range(len(PRINTER_HEAD_SIZE)):
                PRINTER_HEAD_SIZE[i] = int(PRINTER_HEAD_SIZE[i])
        if line_split[0] == "PRINT_BED_EDGE":
            PRINT_BED_EDGE = int(line_split[1])
        if line_split[0] == "PRINT_MIN_DISTANCE":
            PRINT_MIN_DISTANCE = int(line_split[1])
    print(PRINTER_HEAD_SIZE)
    print(PRINT_BED_EDGE)
    print(PRINT_MIN_DISTANCE)
def get_default_distance_params():
    res_dict = {}
    res_dict["PRINTER_HEAD_SIZE"] = PRINTER_HEAD_SIZE
    res_dict["PRINT_BED_EDGE"] = PRINT_BED_EDGE
    res_dict["PRINT_MIN_DISTANCE"] = PRINT_MIN_DISTANCE
    return res_dict
def arrange_models(XML_file,model_path,num_models=-1,distance_params={}):
    
    if "PRINTER_HEAD_SIZE" in distance_params:
        printer_head_size = distance_params["PRINTER_HEAD_SIZE"]
    else:
        printer_head_size = PRINTER_HEAD_SIZE
    if "PRINT_MIN_DISTANCE" in distance_params:
        print_min_distance = distance_params["PRINT_MIN_DISTANCE"]
    else:
        print_min_distance = PRINT_MIN_DISTANCE
    if "PRINT_BED_EDGE" in distance_params:
        print_bed_edge = distance_params["PRINT_BED_EDGE"]
    else:
        print_bed_edge = PRINT_BED_EDGE
    
    floor_x_val = float(read_value(XML_file,"./strokeXoverride"))
    floor_y_val = float(read_value(XML_file,"./strokeYoverride"))
    
    floor_x_min = print_bed_edge
    floor_x_max = floor_x_val - print_bed_edge
    floor_x_center = (floor_x_min + floor_x_max) / 2.0

    floor_y_min = print_bed_edge
    floor_y_max = floor_y_val - print_bed_edge
    floor_y_center = (floor_y_min + floor_y_max) / 2.0
    
    [x_min,x_max,y_min,y_max,z_min,z_max] = get_bounding_box(model_path)
    bbx = x_max - x_min
    bby = y_max - y_min
    bbz = z_max - z_min


    half_bbx = bbx/2
    half_bby = bby/2

    obj_off_x = (x_max + x_min) / 2.0
    obj_off_y = (y_max + y_min) / 2.0

    print("BBX BBY + %f %f"%(bbx,bby))
    print(bbx + printer_head_size[0] + print_min_distance)

    # This centers items on plate
    num_x = 0
    num_y = 0
    x_pos = floor_x_min
    y_pos = floor_y_min
    while x_pos + bbx <= floor_x_max:
        num_x += 1
        x_pos += bbx + print_min_distance + printer_head_size[0]
    while y_pos + bby <= floor_y_max:
        num_y += 1
        y_pos += bby + print_min_distance + printer_head_size[2]

    #If more models can fit than are being used
    if num_models > 0 and num_models < num_x*num_y:
        temp_x=0
        temp_y=0
        while True:
            if temp_x + 1 <= num_x:
                temp_x += 1
                if temp_x * temp_y > num_models:
                    break
            if temp_y + 1 <= num_y:
                temp_y += 1
                if temp_x * temp_y >= num_models:
                    break
        num_x = temp_x
        num_y = temp_y


    # This centers items on plate
    print_center_off = [0,0]
    print_center_off[0] = (bbx * num_x + (printer_head_size[0] + print_min_distance) * (num_x - 1)) / 2.0
    print_center_off[1] = (bby * num_y + (printer_head_size[2] + print_min_distance) * (num_y - 1)) / 2.0


    temp_x = (floor_x_val - ( print_bed_edge*2 + bbx * num_x + (printer_head_size[0] + print_min_distance) * (num_x - 1)))/2.0
    temp_y = (floor_y_val - (print_bed_edge*2 + bby * num_y + (printer_head_size[0] + print_min_distance) * (
    num_y - 1))) / 2.0


    print("TEMP = %f,%f"%(temp_x,temp_y))
    print("CENTER = %f,%f"%(floor_x_center ,floor_y_center ))
    print("OBJ_OFFS = %f,%f"%(obj_off_x,obj_off_y))
    print("OFFS = %f,%f"%(print_center_off[0],print_center_off[1]))

    print_center_off[0] -= floor_x_center
    print_center_off[1] -= floor_y_center

    print("%f<->%f,%f<->%f"%(floor_x_min,floor_x_max,floor_y_min,floor_y_max))
    
    arranged_models = np.zeros([num_x*num_y,2])
    y_off = floor_y_min + half_bbx
    for i in range(num_y):
        x_off = floor_x_min + half_bby
        for j in range(num_x):
            arranged_models[i*num_x+j,0] = x_off +temp_x#- print_center_off[0]
            arranged_models[i*num_x+j,1] = y_off +temp_y#- print_center_off[1]
            x_off += bbx + printer_head_size[0] + print_min_distance
        y_off += bby + printer_head_size[2]  + print_min_distance

    print("ARRANGED MODELS")
    print(len(arranged_models))
    print(arranged_models)

    return arranged_models
    
def get_max_objects(XML_file,model_path,distance_params={}):
    arranged_models = arrange_models(XML_file,model_path,distance_params)
    arr_size = arranged_models.shape
    return arr_size[0]

def get_bounding_box(model_file):
    obj = stl.mesh.Mesh.from_file(model_file)

    minx = maxx = miny = maxy = minz = maxz = None
    for p in obj.points:
        # p contains (x, y, z)
        if minx is None:
            minx = p[stl.Dimension.X]
            maxx = p[stl.Dimension.X]
            miny = p[stl.Dimension.Y]
            maxy = p[stl.Dimension.Y]
            minz = p[stl.Dimension.Z]
            maxz = p[stl.Dimension.Z]
        else:
            maxx = max(p[stl.Dimension.X], maxx)
            minx = min(p[stl.Dimension.X], minx)
            maxy = max(p[stl.Dimension.Y], maxy)
            miny = min(p[stl.Dimension.Y], miny)
            maxz = max(p[stl.Dimension.Z], maxz)
            minz = min(p[stl.Dimension.Z], minz)
    return minx, maxx, miny, maxy, minz, maxz

def display_coords():
    while(True):
        print("Mouse pos %s"%(str(pyautogui.position())))
        print("Screen size %s"%(str(pyautogui.size())))
        minmaxloc = pyautogui.locateOnScreen(SAMPLE_IMAGE_DIR + "minimize_button.png")
        print(minmaxloc)
        time.sleep(1)

if __name__ == "__main__":
    time.sleep(1)
    print(locate_button_center("cur_model_color.png", bypass=False))
    
    
    
    
    
    