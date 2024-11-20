import tkinter

from tkinter import filedialog
from project import ampersandProject
from primitives import ampersandPrimitives, ampersandIO
import ampersandAPI
from headers import get_ampersand_header
import os

def ampersand_dialog():
    print("AmpersandCFD")
    root = tkinter.Tk()
    
    #root.withdraw()
    menu_bar = tkinter.Menu(root)
    
    # File menu
    file_menu = tkinter.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Create", command=lambda: print("New File"))
    file_menu.add_command(label="Open", command=lambda: ampersandAPI.open_project(ampersandPrimitives.ask_for_directory()))
    file_menu.add_command(label="Save", command=lambda: print("Save File"))
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)
    menu_bar.add_cascade(label="File", menu=file_menu)
    
    # Edit menu
    edit_menu = tkinter.Menu(menu_bar, tearoff=0)
    edit_menu.add_command(label="Undo", command=lambda: print("Undo"))
    edit_menu.add_command(label="Redo", command=lambda: print("Redo"))
    edit_menu.add_separator()
    edit_menu.add_command(label="Cut", command=lambda: print("Cut"))
    edit_menu.add_command(label="Copy", command=lambda: print("Copy"))
    edit_menu.add_command(label="Paste", command=lambda: print("Paste"))
    menu_bar.add_cascade(label="Edit", menu=edit_menu)
    
    # Help menu
    help_menu = tkinter.Menu(menu_bar, tearoff=0)
    help_menu.add_command(label="About", command=lambda: print("About"))
    menu_bar.add_cascade(label="Help", menu=help_menu)

    frame = tkinter.Frame(root)
    frame.pack(pady=10)
    frame2 = tkinter.Frame(root)
    frame2.pack(pady=10)

    frame3 = tkinter.Frame(root)
    frame3.pack(pady=10)

    import_stl_button = tkinter.Button(frame, text="Import STL", command=lambda: print("Import STL"))
    import_stl_button.pack(side=tkinter.LEFT, padx=5)

    sphere_button = tkinter.Button(frame, text="Sphere", command=lambda: print("Sphere"))
    sphere_button.pack(side=tkinter.LEFT, padx=5)

    box_button = tkinter.Button(frame, text="Box", command=lambda: print("Box"))
    box_button.pack(side=tkinter.LEFT, padx=5)

    flow_type = tkinter.StringVar(value="Internal")
    tkinter.Label(frame, text="Flow Type:").pack(side=tkinter.LEFT, padx=5)
    internal_flow_radio = tkinter.Radiobutton(frame2, text="Internal Flow", variable=flow_type, value="Internal")
    internal_flow_radio.pack(side=tkinter.LEFT, padx=5)

    external_flow_radio = tkinter.Radiobutton(frame2, text="External Flow", variable=flow_type, value="External")
    external_flow_radio.pack(side=tkinter.LEFT, padx=5)

    on_ground_var = tkinter.BooleanVar()
    on_ground_check = tkinter.Checkbutton(frame2, text="On Ground", variable=on_ground_var)
    on_ground_check.pack(side=tkinter.LEFT, padx=5)

    run_simulation_button = tkinter.Button(frame2, text="Run Simulation", command=lambda: print("Run Simulation"))
    run_simulation_button.pack(side=tkinter.LEFT, padx=5)
    
    root.config(menu=menu_bar)
    root.mainloop()

if __name__ == "__main__":
    ampersand_dialog()