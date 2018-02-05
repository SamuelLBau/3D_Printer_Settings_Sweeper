import pyautogui
import numpy as np
import struct
import stl
import time
from math import ceil
import os
import shutil
import tkMessageBox

from XML_handler import read_value,generate_XML_file

ABS_DIR = os.path.dirname(os.path.realpath(__file__))

SRC_DIR = ABS_DIR + "/src/"
SAMPLE_IMAGE_DIR = SRC_DIR + "Simplify_images/"
FACTORY_DIR = SRC_DIR + "factory_files/"
PRINT_BED_EDGE = 10
PRINTER_HEAD_SIZE = [50,50] #[x,y]rectangle (max edge length)

TYPE_DELAY = .01
TAB_DELAY = .1
WINDOW_DELAY = .2

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

def locate_button_center(file_name,bypass=True):
    global BUTTON_LOCATIONS
    if (not file_name in BUTTON_LOCATIONS) or not bypass:
        time.sleep(WINDOW_DELAY)
        loc = pyautogui.locateOnScreen(SAMPLE_IMAGE_DIR + file_name)
        center = [loc[0] + loc[2] / 2, loc[1] + loc[3] / 2]
        BUTTON_LOCATIONS[file_name] = center
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
    loc = locate_button_center("cur_model_color.png",bypass=False)
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

def generate_factories(XML_data,model,prefix):
    pos_list = arrange_models(XML_data[0], model)
    items_per_factory = pos_list.shape[0]
    num_objects = len(XML_data)
    num_factories = int(ceil( float(num_objects) / float(len(pos_list))))

    print(model)

    objects_written = 0
    base_folder = FACTORY_DIR+prefix
    if os.path.isdir(base_folder):
        shutil.rmtree(base_folder, ignore_errors=True)
    os.mkdir(base_folder)
    base_folder = base_folder + "/"

    open_Simplify3D()
    for fac_num in range(num_factories):
        cur_fac_dir = base_folder + str("%s%d"%(prefix,fac_num))
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
        time.sleep(2)

    close_Simplify3D()
def arrange_models(XML_file,model_path):
    floor_x_val = float(read_value(XML_file,"./strokeXoverride"))
    floor_x_center = floor_x_val/2.0
    floor_x_min = PRINT_BED_EDGE
    floor_x_max = floor_x_val - PRINT_BED_EDGE

    floor_y_val = float(read_value(XML_file,"./strokeYoverride"))
    floor_y_center = floor_y_val/2.0
    floor_y_min = PRINT_BED_EDGE
    floor_y_max = floor_y_val - PRINT_BED_EDGE
    
    [x_min,x_max,y_min,y_max,z_min,z_max] = get_bounding_box(model_path)
    bbx = x_max - x_min
    bby = y_max - y_min
    bbz = z_max - z_min

    obj_offx = (x_max + x_min) / 2.0
    obj_offy = (y_max + y_min) / 2.0
    obj_offz = (z_max + z_min) / 2.0


    half_bbx = bbx/2
    half_bby = bby/2
    
    num_x = np.floor((floor_x_max-floor_x_min)/(bbx + PRINTER_HEAD_SIZE[0]/2)).astype(np.int)
    num_y = np.floor((floor_y_max-floor_y_min)/(bby + PRINTER_HEAD_SIZE[1]/2)).astype(np.int)
    
    arranged_models = np.zeros([num_x*num_y,2])
    x_off = floor_x_min + half_bbx
    for i in range(num_x):
        y_off = floor_y_min + half_bby
        for j in range(num_y):
            arranged_models[i*num_y+j,0] = x_off - obj_offx
            arranged_models[i*num_y+j,1] = y_off - obj_offy
            y_off += bby + PRINTER_HEAD_SIZE[1]/2
        x_off += bbx + PRINTER_HEAD_SIZE[0]/2

    print(len(arranged_models))
    return arranged_models
    
def get_max_objects(XML_file,model_path):
    arranged_models = arrange_models(XML_file,model_path)
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
    
    
    
    
    
    