from typing import Tuple
import customtkinter as ctk
import json
from CTkTable import *
import threading
import time

class ManualWindow(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()

        # self.focus = focus
        # self.message = message
        self.init_ui()
    
    def init_ui(self):
        self.geometry("600x300")
        self.title('mode settings')
        self.resizable(False, False)
        self.MainFrame = ctk.CTkFrame(self, fg_color="transparent")
        self.MainFrame.grid(row=0, column=0)
        self.label = ctk.CTkLabel(self.MainFrame, "Please select mode configuration.")
        self.label.grid(row=0, column=0, sticky="nsew")

        self.new_protocol_button = ctk.CTkButton()
        self.protocol_adjust_button = ctk.CTkButton()
        # self.grab_set()
