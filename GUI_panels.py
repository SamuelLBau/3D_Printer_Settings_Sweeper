import Tkinter as tk
import tkFileDialog

from copy import deepcopy

from XML_handler import XML_load_file,XML_get_attributes,XML_get_data, \
        XML_list_nodes,XML_is_leaf,XML_get_leaf_data,XML_get_tag,XML_data_type\
        
        

from XML_handler import etree_to_dict

class ScrolledFrame(tk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling

    """
    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)            

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = tk.Scrollbar(self, orient="vertical")
        vscrollbar.pack(fill="y", side="right", expand=False)
        hscrollbar = tk.Scrollbar(self, orient="horizontal")
        hscrollbar.pack(fill="x", side="bottom", expand=False)
        
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,bg="purple",
                        yscrollcommand=vscrollbar.set,xscrollcommand=hscrollbar.set)
        #canvas.config(scrollregion=canvas.bbox("all"))
        canvas.config(width=300,height=10000,scrollregion=(0,0,1000,8000))
        canvas.pack(side="left", fill="both", expand=True)
        vscrollbar.config(command=canvas.yview)
        hscrollbar.config(command=canvas.xview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(canvas)
        interior_id = canvas.create_window((0, 0), window=interior,
                                           anchor="nw")
        self.canv = self.interior
        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
                #print("HERE")
                #self.interior.header_frame.pack(side="top")
                #self.interior.data_frame.pack(side="bottom")
            if interior.winfo_reqheight() != canvas.winfo_height():
                # update the canvas's height to fit the inner frame
                canvas.config(height=interior.winfo_reqheight())
                #print("HEREH")
                #self.interior.header_frame.pack(side="top")
                #self.interior.data_frame.pack(side="bottom")
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            canvas.config(scrollregion=canvas.bbox("all"))
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                #canvas.itemconfigure(interior_id, width=canvas.winfo_width())
                pass
            if interior.winfo_reqheight() != canvas.winfo_height():
                # update the inner frame's height to fill the canvas
                #canvas.itemconfigure(interior_id, height=canvas.winfo_height())
                pass
            canvas.config(scrollregion=canvas.bbox("all"))
            #canvas.update_idletasks()
        canvas.bind('<Configure>', _configure_canvas)
        
class header_frame(tk.Frame):

    def __init__(self,master):
        tk.Frame.__init__(self,master,bg="blue")
        self.master = master
        self.base_profile_LABEL = tk.Label(self,text = "Base profile name: ")
        self.base_profile_SV    = tk.StringVar()
        self.base_profile2_LABEL= tk.Label(self,textvariable=self.base_profile_SV)
        self.profile_name_LABEL = tk.Label(self,text="Profile name prefix: ")
        self.profile_name_SV    = tk.StringVar()
        self.profile_name_ENTRY = tk.Entry(self,textvariable=self.profile_name_SV)
        self.save_BUTTON        = tk.Button(self,text="Save .fff files",command=self.save_button_press)
        self.load_BUTTON        = tk.Button(self,text="Load .fff file",command=self.load_button_press)
        
        self.base_profile_SV.set("")
        self.profile_name_SV.set("")
        
        self.base_profile_LABEL.grid (row=0,column=0)
        self.base_profile2_LABEL.grid(row=0,column=1)
        self.profile_name_LABEL.grid(row=1,column=0)
        self.profile_name_ENTRY.grid(row=1,column=1)
        self.save_BUTTON.grid(row=2,column=0)
        self.load_BUTTON.grid(row=2,column=1)
        
        
        
    def save_button_press(self):
        self.master.save_file()
    def load_button_press(self):
        self.master.load_new_file()        
    def get_profile_prefix(self=None):
        return self.profile_name_SV.get()
    def set_profile_prefix(self,value):
        self.base_profile_SV.set(value)
    
    
class parameter_frame(tk.Frame):
    #This assumes that incoming data (from initialize panel) is not a tree leaf
    DEFAULT_TAB_OFFSET = 5
    
    
    
    def __init__(self,master,level=0):
        tk.Frame.__init__(self,master,bg="red")#,bd=3,highlightbackground="black")
        self.sub_panels = []
        self.attribute_panels = []
    
    def initialize_panel(self,data,offset=DEFAULT_TAB_OFFSET):

        self.clear_panels()
        self.sub_panels = []#This should be done in clear_panels()
        self.attribute_panels = []
        attributes  = XML_get_attributes(data)
        sub_nodes   = XML_get_data(data)
        tag         = XML_get_tag(data)
        name_LABEL  = tk.Label(self,text=tag,bg="pink")
        name_LABEL.grid(row=0,sticky="ew")
        for item in attributes:
            if tag =="profile" and item=="name":
                continue
            pan_data = [item,attributes[item]]
            cur_panel = value_frame(self)
            cur_panel.initialize_panel(pan_data)
            self.attribute_panels.append(cur_panel)
            
        for id,item in enumerate(sub_nodes):
            cur_panel = None
            if(XML_is_leaf(item)):
                cur_panel = value_frame(self)
                cur_panel.initialize_panel(item)
            else:
                cur_panel = parameter_frame(self)
                cur_panel.initialize_panel(item,offset+self.DEFAULT_TAB_OFFSET)
            self.sub_panels.append(cur_panel)
        
        n_attr = len(self.attribute_panels)
        for id,item in enumerate(self.attribute_panels):
                item.grid(row=id+1,sticky="ew")
        for id,item in enumerate(self.sub_panels):
                item.grid(row=id+1+n_attr,sticky="ew",padx=[offset,0])
    def get_data(self,data):
        #TODO: Read in attributes
        
        #TODO: Read in sub panels
        pass
    
    def collapse_panel(self):
        pass
    def expand_panel(self):
        pass
    
    def clear_panels(self):
        n_items = len(self.attribute_panels)
        for id in range(n_items-1,-1,-1):
            self.attribute_panels[id].clear_panels()
            self.attribute_panels[id].grid_forget()
            self.attribute_panels[id].destroy()
        n_items = len(self.sub_panels)
        for id in range(n_items-1,-1,-1):
            self.sub_panels[id].clear_panels()
            self.sub_panels[id].grid_forget()
            self.sub_panels[id].destroy()
        self.grid()

class value_frame(tk.Frame):
    def __init__(self,master):
        tk.Frame.__init__(self,master,bg="green",bd=2,highlightbackground="black")#,bd=3,highlightbackground="black")
        self.data_type = type(None)
        self.initialized= False
        self.widgets = []
        
        self.SV0 = tk.StringVar()
        self.SV1 = tk.StringVar()
        self.SV2 = tk.StringVar()
    
    def clear_panels(self):
        num_items = len(self.widgets)
        for i in range(num_items-1,-1,-1):
            self.widgets[i].destroy()
        self.widgets = []
        
        self.SV0.set("")
        self.SV1.set("")
        self.SV2.set("")
        
        
    def get_data(self):
        #TODO: get data in XML tree format
        pass
    def initialize_panel(self,data):
        if not isinstance(data,list):
            data = XML_get_leaf_data(data)
        new_str = str("%s=%s"%(data[0],data[1]))
        
        self.data_type = XML_data_type(data[1])
        if self.data_type == type(""):
            self.initialize_str_panel(data)
            self.initialized = True
        elif self.data_type == type(1.2):
            self.initialize_float_panel(data)
            self.initialized = True
        elif self.data_type == type(1):
            self.initialize_int_panel(data)
            self.initialized = True
        elif self.data_type == type(None):
            self.initialize_none_panel(data)
            self.initialized = True
        else:
            print("DATA TYPE NOT RECOGNIZED, FAILED TO INITIALIZE PANEL")
            self.initialized = False
        
    def initialize_str_panel(self,data):
        tag = data[0]
        value = data[1]
        self.feature_LABEL = tk.Label(self,text=data[0],width=30,anchor="w",\
            font="helvetica 9 bold")
        self.widgets.append(self.feature_LABEL)
        self.feature_ENTRY = tk.Entry(self,textvariable=self.SV0,width=30)
        self.widgets.append(self.feature_ENTRY)
        
        self.SV0.set(data[1])
        self.SV1.set("")
        self.SV2.set("")
        
        self.feature_LABEL.pack(side="left")
        self.feature_ENTRY.pack(side="left")
        
    def initialize_float_panel(self,data):
        tag = data[0]
        value = data[1]
        self.feature_LABEL = tk.Label(self,text=data[0],width=30,anchor="w",\
            font="helvetica 9 bold")
        self.widgets.append(self.feature_LABEL)
        self.from_LABEL = tk.Label(self,text="from")
        self.widgets.append(self.from_LABEL)
        self.to_LABEL = tk.Label(self,text="to")
        self.widgets.append(self.to_LABEL)
        self.interval_LABEL = tk.Label(self,text="int")
        self.widgets.append(self.interval_LABEL)
        
        self.SV0.set(data[1])
        
        self.from_ENTRY = tk.Entry(self,textvariable=self.SV0,width=7)
        self.widgets.append(self.from_ENTRY)
        self.to_ENTRY = tk.Entry(self,textvariable=self.SV1,width=7)
        self.widgets.append(self.to_ENTRY)
        self.interval_ENTRY = tk.Entry(self,textvariable=self.SV2,width=7)
        self.widgets.append(self.interval_ENTRY)
        
        self.feature_LABEL.pack(side="left")
        self.from_LABEL.pack(side="left")
        self.from_ENTRY.pack(side="left")
        self.to_LABEL.pack(side="left")
        self.to_ENTRY.pack(side="left")
        self.interval_LABEL.pack(side="left")
        self.interval_ENTRY.pack(side="left")
    def initialize_int_panel(self,data):
        self.initialize_float_panel(data)
    def initialize_none_panel(self,data):
        data[1] = ""
        self.initialize_str_panel(data)

class main_app(ScrolledFrame):
    
    def __init__(self,master,init_file=""):
        ScrolledFrame.__init__(self,master)
        self.XML_data = None
        
        self.create_widgets()
        self.pack()
        
        if not init_file == "":
            self.load_new_file(init_file)
            
        #FOR TESTING, AUTOMATICALLY LOAD A NEW FILE
        self.load_new_file()
        
    def load_new_file(self=None):
        #TODO: open up a file dialog to select a file
        
        #FOR TESTING, AUTOMATICALLY LOAD THIS FILE
        #file_name = tkFileDialog.askopenfilename(initialdir="./src")
        file_name = "./src/Strawson's Ultimaker 2+ Settings.fff"
        
        
        print("Attempting to load %s"%(file_name))
        if file_name is None:
            print("No value returned from load dialog, returning")
            return
        self.XML_data = XML_load_file(file_name)
        if self.XML_data is None:
            print("Unknown error loading XML data")
            return
        
        attributes = XML_get_attributes(self.XML_data)
        self.header_frame.set_profile_prefix(attributes["name"])

        #This updates the sub panel
        #self.data_frame = parameter_frame(self)
        self.data_frame.initialize_panel(self.XML_data)
        
        self.data_frame.pack(side="bottom")
        #self.canv.pack()
        #print(self.canv.winfo_reqwidth(),self.canv.winfo_reqheight())
    def save_file(self=None):
        print("Save file pressed")
        #TODO: open up a file dialog to select a file name
        #TODO: generate an XML tree from lower panels
        #Save the resulting XML
        pass
        
    def create_widgets(self):
        self.canv.load_new_file = self.load_new_file
        self.canv.save_file = self.save_file

        self.header_frame = header_frame(self.canv)
        self.header_frame.pack(side="top",anchor="w")
        
        self.data_frame = parameter_frame(self.canv)
        self.data_frame.pack(side="bottom",fill="x",expand=1)

    def canv_configure(self,event):
        pass