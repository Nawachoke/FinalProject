import tkinter
from typing import Optional, Tuple, Union
import customtkinter as ctk
import sys
import json
# sys.path.insert(0, 'C:/Project/FinalProject/ImageProcessing/TrayFinder2.py')
from ImageProcessing import TrayFinder2 as TF
import pandas as pd
import numpy as np
from CTkTable import *
import threading

ctk.set_appearance_mode("System") # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue") # Themes: "blue" (standard), "green", "dark-blue"

class askyesno(ctk.CTkToplevel):
    def __init__(self, message, focus=True):
        super().__init__()
        # self.master = master
        self.focus = focus
        self.message = message
        self.button_clicked = False
        self.init_ui()

    def init_ui(self):
        self.geometry("300x150")
        self.title("Confirmation")
        self.resizable(False, False)

        message_label = ctk.CTkLabel(self, text=self.message)
        message_label.pack(pady=10)

        self.grab_set()

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10)

        yes_button = ctk.CTkButton(button_frame, text="Yes", command=lambda: self.button_click(True))
        yes_button.pack(side="left", padx=10)

        no_button = ctk.CTkButton(button_frame, text="No", command=lambda: self.button_click(False))
        no_button.pack(side = "right", padx=10)

    def button_click(self, button):
        self.button_clicked = button
        self.grab_release()
        self.destroy()

    def get_result(self):
        if self.focus:
            self.grab_set()
        self.wait_window()
        return self.button_clicked

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Cells stain controller")
        self.geometry(f"{1200}x{640}")
        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2,3), weight=0)
        self.grid_rowconfigure((0,1,2),weight=1)
        
        #create sidebar frame with widgets
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4,sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Cells Staining Machine", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20,10))
        self.mode_optionmenu_label = ctk.CTkLabel(self.sidebar_frame, text="Staining mode", anchor="w")
        self.mode_optionmenu_label.grid(row=1, column=0, padx=20, pady=10)
        self.mode_optionmenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["IHC", "H&E"], command=self.mode_event)
        self.mode_optionmenu.grid(row=2, column=0, padx=20, pady=10)
        self.start_button = ctk.CTkButton(self.sidebar_frame, text="START", command=self.start_event, font=ctk.CTkFont(size=16))
        self.start_button.grid(row = 3, column=0, padx=20, pady=10)
        self.stop_button = ctk.CTkButton(self.sidebar_frame, text="STOP", command=self.stop_event, font=ctk.CTkFont(size=16))
        self.stop_button.grid(row=4, column = 0, padx=20, pady=10)
        self.pause_button = ctk.CTkButton(self.sidebar_frame, text="PAUSE", command=self.pause_event, font=ctk.CTkFont(size=16))
        self.pause_button.grid(row=5, column=0, padx=20, pady=10)
        self.image_button = ctk.CTkButton(self.sidebar_frame, text="IMAGE", command=self.image_event, font=ctk.CTkFont(size=16))
        self.image_button.grid(row=6, column=0, padx=20, pady=10)
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance mode", anchor="w")
        self.appearance_mode_label.grid(row=8, column=0, padx=20, pady=(10,0))
        self.appearance_mode_optionmenu = ctk.CTkOptionMenu(self.sidebar_frame ,values=["Light", "Dark"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionmenu.grid(row=9, column=0, padx=20, pady=(10,10))
        self.scaling_label = ctk.CTkLabel(self.sidebar_frame, text="UI Scaling", anchor="w")
        self.scaling_label.grid(row=10, column=0, padx=20, pady=(10,0))
        self.scaling_optionmenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"], command=self.change_scaling_event)
        self.scaling_optionmenu.grid(row=11, column=0, padx=20, pady=(10,20))

        #create progress bar
        self.progress_bar_frame = ctk.CTkFrame(self)
        self.progress_bar_frame.grid_columnconfigure(8)
        self.progress_bar_frame.grid(row=3, column = 1, columnspan=3, padx=10, pady=(20,20), sticky="nsew")
        self.progress_bar_label = ctk.CTkLabel(self.progress_bar_frame, text="Progression :")
        self.progress_bar_label.grid(row=0, column=0, padx=10, pady=(10, 10))
        self.progress_bar = ctk.CTkProgressBar(self.progress_bar_frame, progress_color="green")
        self.progress_bar.grid(row=0, column=1, columnspan=6, padx=10, pady=10)
        
        #create table frame


        # set default values
        self.appearance_mode_optionmenu.set("Dark")
        self.scaling_optionmenu.set("100")
        self.mode_optionmenu.set("MODE")

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)
    
    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def image_event(self):
        pass
    
    def start_event(self):
        pass

    def stop_event(self):
        pass

    def pause_event(self):
        pass

    def mode_event(self, mode : str):
        self.mode = mode
        if mode == "H&E":
            warn_text = "Start with H & E mode"
            mode_number = 1
        elif mode == "":
            warn_text = "Start with IHC mode"
            mode_number = 2
        else:
            pass

        Mode_confirm = askyesno(message=warn_text, focus=True)
        answer = Mode_confirm.get_result()

        if answer == True:
            self.mode_data = self.Read_Data(mode_number)
            
    
    def Read_Data(self, mode_number : str):
        file = open("C:/Project/FinalProject/MainPackage/mode_conf.json")
        data = json.load(file)
        mode_name = data['mode ' + mode_number]['name']

        self.Mode_data = pd.read_json("C:/Project/seniorProject/mainProgram/mode_conf.json")

        self.monitoring_data = pd.DataFrame({  'solution'  : self.All_mode_data['mode ' + mode_number]['solution'],
                                                'time'     : self.All_mode_data['mode ' + mode_number]['time'],
                                                'cycle'    : self.All_mode_data['mode ' + mode_number]['cycle']})
        
        return mode_name

    def DataOverwrite(self):
        pass

if __name__ == "__main__":
    app = App()
    app.mainloop()