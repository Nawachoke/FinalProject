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
import os
from PIL import Image

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
        self.geometry("300x200")
        
        self.title("Confirmation")
        self.resizable(False, False)
        message_label = ctk.CTkLabel(self, text=self.message)
        message_label.pack(pady=10)
        self.grab_set()

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=10)

        self.warn_image = ctk.CTkImage(Image.open("C:/Project/FinalProject/image/warning-sign.png"), size=(50,50))
        warn = ctk.CTkLabel(button_frame,image=self.warn_image, text="")
        warn.pack(side="top", padx=10, pady=10)
        yes_button = ctk.CTkButton(button_frame, text="Yes", command=lambda: self.button_click(True))
        yes_button.pack(side="left", padx=10, pady=20)

        no_button = ctk.CTkButton(button_frame, text="No", command=lambda: self.button_click(False))
        no_button.pack(side = "right", padx=10, pady=20)

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
        self.iconbitmap("C:/Project/FinalProject/image/icons8-cell-50.ico")

        self.percentage_data = str("xx")

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
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Control Panel", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20,10))
        self.mode_optionmenu_label = ctk.CTkLabel(self.sidebar_frame, text="Staining mode", anchor="w")
        self.mode_optionmenu_label.grid(row=1, column=0, padx=20, pady=10)
        self.mode_optionmenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["IHC", "H&E"], command=self.mode_event)
        self.mode_optionmenu.grid(row=2, column=0, padx=20, pady=10)
        self.image_button = ctk.CTkButton(self.sidebar_frame, text="IMAGE", command=self.image_event, font=ctk.CTkFont(size=16))
        self.image_button.grid(row=3, column=0, padx=20, pady=10)
        self.start_button = ctk.CTkButton(self.sidebar_frame, text="START", command=self.start_event, font=ctk.CTkFont(size=16))
        self.start_button.grid(row = 4, column=0, padx=20, pady=10)
        self.stop_button = ctk.CTkButton(self.sidebar_frame, text="STOP", command=self.stop_event, font=ctk.CTkFont(size=16))
        self.stop_button.grid(row=5, column = 0, padx=20, pady=10)
        self.pause_button = ctk.CTkButton(self.sidebar_frame, text="PAUSE", command=self.pause_event, font=ctk.CTkFont(size=16))
        self.pause_button.grid(row=6, column=0, padx=20, pady=10)
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance mode", anchor="w")
        self.appearance_mode_label.grid(row=8, column=0, padx=20, pady=(10,0))
        self.appearance_mode_optionmenu = ctk.CTkOptionMenu(self.sidebar_frame ,values=["Light", "Dark", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionmenu.grid(row=9, column=0, padx=20, pady=(10,10))
        self.scaling_label = ctk.CTkLabel(self.sidebar_frame, text="UI Scaling", anchor="w")
        self.scaling_label.grid(row=10, column=0, padx=20, pady=(10,0))
        self.scaling_optionmenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"], command=self.change_scaling_event)
        self.scaling_optionmenu.grid(row=11, column=0, padx=20, pady=(10,20))

        # create progress bar
        self.progress_bar_frame = ctk.CTkFrame(self)
        # self.progress_bar_frame.grid_columnconfigure(8)
        self.progress_bar_frame.grid(row=3, column = 1, columnspan=2, padx=10, pady=(20,20), sticky="nsew")
        self.progress_bar_label = ctk.CTkLabel(self.progress_bar_frame, text="Progression :")
        self.progress_bar_label.grid(row=0, column=0, padx=10, pady=(10, 10))
        self.progress_bar = ctk.CTkProgressBar(self.progress_bar_frame, progress_color="green", width=700)
        self.progress_bar.grid(row=0, column=1, columnspan=6, padx=10, pady=10, sticky="nsew")
        self.percentage_label = ctk.CTkLabel(self.progress_bar_frame, text=f"{self.percentage_data} / 100%")
        self.percentage_label.grid(row=0, column=8, sticky='e')
        # self.progressbar = ctk.CTkProgressBar(self, progress_color="green")
        # self.progressbar.grid(row=2, column=1, columnspan=1, padx=10, pady=10, sticky="nsew")
        # self.progress_bar.start()

        #Monitoring frame
        self.monitoring_frame = ctk.CTkFrame(self, width=100, corner_radius=20)
        self.monitoring_frame.grid(row=0, column=1, padx=20, pady=20, rowspan=2, sticky="nsew")
        self.monitor_label = ctk.CTkLabel(self.monitoring_frame, text="Status monitor", font=ctk.CTkFont(size=24, weight="bold"))
        self.monitor_label.grid(row=0, column=0, sticky="news")

        self.Protocol_label = ctk.CTkLabel(self.monitoring_frame, text="Protocol : ", font=('Arial', 16, 'bold'))
        self.Status_time_label = ctk.CTkLabel(self.monitoring_frame, text="Status time : ", font=('Arial', 16, 'bold'))
        self.Current_solution_label = ctk.CTkLabel(self.monitoring_frame, text="Current solution : ", font=('Arial', 16, 'bold'))
        self.Next_solution_label = ctk.CTkLabel(self.monitoring_frame, text ="Next solution : ", font=('Arial', 16, 'bold'))
        self.Left_rack_label = ctk.CTkLabel(self.monitoring_frame, text="Left rack : ", font=('Arial', 16, 'bold'))
        mf = 0
        for status_widget in self.monitoring_frame.winfo_children() : 
            status_widget.grid_configure(row=mf, column=0, sticky = "w", padx=20, pady=20)
            mf+=1

        self.Status_time_data = ctk.CTkLabel(self.monitoring_frame, text= "", anchor="w", font=('Arial', 16, 'bold'))
        self.Status_time_data.grid(row = 2, column=1, sticky = "w", padx=20, pady=20)
        self.Current_solution_data = ctk.CTkLabel(self.monitoring_frame, text="", anchor="w", font=('Arial', 16, 'bold'))
        self.Current_solution_data.grid(row = 3, column = 1 , sticky="w", padx=20, pady=20)
        self.Next_solution_data = ctk.CTkLabel(self.monitoring_frame, text= "", anchor="w", font=('Arial', 16, 'bold'))
        self.Next_solution_data.grid(row=4, column=1, sticky = 'w', padx=20, pady=20)
        self.Left_rack_data = ctk.CTkLabel(self.monitoring_frame, text="", anchor="w", font=('Arial', 16, 'bold'))
        self.Left_rack_data.grid(row=5, column=1, sticky="w", padx=20, pady=20)

        #Table frame
        self.Table_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.Table_frame.grid(row=0, column=2)

        # set default values
        self.appearance_mode_optionmenu.set("Dark")
        self.scaling_optionmenu.set("100")
        self.mode_optionmenu.set("MODE")
        self.progress_bar.set(0)

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

    def show_table(self):
        RawData = [self.monitoring_data['solution'],
                   self.monitoring_data['time'],
                   self.monitoring_data['cycle']]
        name_list = ['solution', 'time', 'cycle']
        pivoted_value = list(map(list, zip(*RawData)))
        pivoted_value.insert(0, name_list)

        self.table = CTkTable(master=self.Table_frame, values=pivoted_value, font=('Arial', 16))
        self.table.grid(row=0, column=2, padx=20, pady=20)

    def mode_event(self, mode : str):
        self.mode = mode
        if mode == "H&E":
            message = "Start with H & E mode"
            mode_number = 1
        elif mode == "IHC":
            message = "Start with IHC mode"
            mode_number = 2
        else:
            pass

        Mode_confirm = askyesno(message=message, focus=True)
        answer = Mode_confirm.get_result()

        if answer == True:
            self.mode_name = self.Read_Data(mode_number)
            self.DestroyTable()
            self.show_table()
            
    
    def Read_Data(self, mode_number):
        file = open("C:/Project/FinalProject/MainPackage/mode_conf.json")
        data = json.load(file)
        mode_name = data['mode ' + str(mode_number)]['name']

        self.Mode_data = pd.read_json("C:/Project/seniorProject/mainProgram/mode_conf.json")

        self.monitoring_data = pd.DataFrame({  'solution'  : self.Mode_data['mode ' + str(mode_number)]['solution'],
                                                'time'     : self.Mode_data['mode ' + str(mode_number)]['time'],
                                                'cycle'    : self.Mode_data['mode ' + str(mode_number)]['cycle']})
        
        return mode_name

    def DataOverwrite(self):
        pass

    def DestroyTable(self):
        for widget in self.Table_frame.winfo_children() :
            widget.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()