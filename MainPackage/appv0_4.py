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

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

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
        self.geometry(f"{800}x{550}")
        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2,3), weight=0)
        self.grid_rowconfigure((0,1,2),weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)
    
    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

if __name__ == "__main__":
    app = App()
    app.mainloop()