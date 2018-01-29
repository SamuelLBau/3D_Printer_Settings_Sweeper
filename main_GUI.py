import Tkinter as tk
import sys

from GUI_panels import *

XML_folder = "./src/"
default_file = XML_folder + "Strawson's Ultimaker 2+ Settings.fff"

def main(input_file):
    root = tk.Tk()
    root.minsize(10,10)
    root.maxsize(500,500)
    app = main_app(master=root)
    app.mainloop()
    root.destroy()

if __name__ == "__main__":
    input_file = default_file
    
    if len(sys.argv) > 1:
        input_file = XML_folder + sys.argv[1]
    main(input_file)