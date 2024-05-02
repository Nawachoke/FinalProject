import glob
import os
import tkinter
from typing import Optional, Tuple, Union
import customtkinter as ctk
import pandas as pd
import numpy as np
from PIL import Image
import json


class ManualWindow(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.folder = "FinalProject/MainPackage/Protocols"

        files = glob.glob(self.folder+"/*")

        self.file_names = [os.path.splitext(os.path.basename(file))[0] for file in files if file.endswith('.json')]

        for file_name in self.file_names:
            print(file_name)

        # self.init_ui()

    # def init_ui(self):
        self.title("Settings")
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.tabview.add("Manual")
        self.tabview.add("Adjustment")

        self.tabview.tab("Manual").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Adjustment").grid_columnconfigure(0, weight=1)
    
        self.mode_option = ctk.CTkOptionMenu(self.tabview.tab("Adjustment") ,values = self.file_names, command=self.mode_event)
        self.mode_option.grid(row=0, column=0, padx=10, pady=10)
        self.save_button = ctk.CTkButton(self.tabview.tab("Adjustment"), text = "SAVE", command=self.save_event)
        self.save_button.grid(row=0, column=2, padx=10, pady=10)



    #set default value
        self.mode_option.set("Protocols")
    def save_event(self):
        extracted_data = []
        for row_data in self.entry_data:
            extracted_row_data = [self.entry.get() for self.entry in row_data]
            extracted_data.append(extracted_row_data)
        print(extracted_data)

    def mode_event(self, mode : str):
        self.entry_data = []
        # pass
        # print(self.folder+'/'+mode+'.json')
        # print(type(mode))
        path = os.path.join(self.folder, mode + '.json')
        file = open(path)
        data = json.load(file)
        # self.mode_data = pd.read_json(path)
        self.data = pd.DataFrame({ 'solution' : data['solution'],
                                    'time': data['time'],
                                    'cycle': data['cycle']})
        
        self.config_frame = ctk.CTkFrame(self.tabview.tab("Adjustment"))
        self.config_frame.grid(row=1, column=0, columnspan = 2)
        self.create_widget()
        # print(self.data)
    def create_widget(self):
        for widget in self.config_frame.winfo_children():
            widget.destroy()
        for index, row in self.data.iterrows():
            self.entry_row_data = []
            for col, value in enumerate(row):
                self.entry = ctk.CTkEntry(self.config_frame)
                self.entry.grid(row=index, column=col, padx=5, pady=5)
                self.entry.insert(index = 0, string= value)
                self.entry_row_data.append(self.entry)
            self.entry_data.append(self.entry_row_data)

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

        self.warn_image = ctk.CTkImage(Image.open("FinalProject/MainPackage/image/warning-sign.png"), size=(50,50))
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
        
    if __name__ == '__main__':
        app = ManualWindow()
        app.mainloop()