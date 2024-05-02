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
        self.folder = "MainPackage/Protocols"

        files = glob.glob(self.folder+"/*")

        self.file_names = [os.path.splitext(os.path.basename(file))[0] for file in files if file.endswith('.json')]

        # for file_name in self.file_names:
        #     print(file_name)
        self.grab_set()
        self.title("Settings")
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.tabview.add("Manual")
        self.tabview.add("Adjustment")

        self.tabview.tab("Manual").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Adjustment").grid_columnconfigure(0, weight=1)

        #Adjustment window
        self.control_frame = ctk.CTkFrame(self.tabview.tab("Adjustment"))
        self.control_frame.grid(row=0 ,column=0)
        self.mode_option = ctk.CTkOptionMenu(self.control_frame, values = self.file_names, command=self.mode_event)
        self.mode_option.grid(row=0, column=0, padx=10, pady=10)
        self.save_button = ctk.CTkButton(self.control_frame, text = "SAVE", command=self.save_event)
        self.save_button.grid(row=0, column=1, padx=10, pady=10)
        self.delete_button = ctk.CTkButton(self.control_frame, text = "DELETE", command=self.delete_event)
        self.delete_button.grid(row=0, column=2, padx=10, pady=10)

        #Manual configuration window
        self.manual_control_frame = ctk.CTkFrame(self.tabview.tab("Manual"))
        self.manual_control_frame.grid(row=0, column=0)
        options = [str(i) for i in range(1, 19)]
        self.rack_number_option = ctk.CTkOptionMenu(self.manual_control_frame, values=options, command=self.rack_amount())
        self.rack_number_option.grid(row=0, column=0, padx=10, pady=10, sticky="se")
        self.clear_button = ctk.CTkButton(self.manual_control_frame, text="CLEAR", command=self.clear_event())
        self.clear_button.grid(row=0, column=1, padx=10, pady=10, sticky="se")
        self.manual_save_button = ctk.CTkButton(self.manual_control_frame, text="SAVE", command=self.save_manual_event())
        self.manual_save_button.grid(row=0, column=2, padx=10, pady=10, sticky="se")
        

    #set default value
        self.mode_option.set("Protocols")
        self.rack_number_option.set("Rack amount")

    def delete_event(self):
        pass
    def save_event(self):

        solution_list, time_list, cycle_list = [],[],[]
        for self.entry_solution, self.entry_time, self.entry_cycle in self.entry_data:
            solution = self.entry_solution.get()
            time = int(self.entry_time.get())
            cycle = int(self.entry_cycle.get())

            solution_list.append(solution)
            time_list.append(time)
            cycle_list.append(cycle)

        json_data = json.dumps({'solution':solution_list, "time":time_list, "cycle":cycle_list}, indent=4)

        with open(self.path, "w") as json_file:
            json_file.write(json_data)

        print("saved successfully!")

    def mode_event(self, mode : str):
        self.entry_data = []
        self.path = os.path.join(self.folder, mode + '.json')
        file = open(self.path)
        data = json.load(file)
        # self.mode_data = pd.read_json(path)
        self.data = pd.DataFrame({ 'solution' : data['solution'],
                                    'time'    : data['time'],
                                    'cycle'   : data['cycle']})
        
        self.config_frame = ctk.CTkFrame(self.tabview.tab("Adjustment"))
        self.config_frame.grid(row=1, column=0, columnspan = 2)
        self.create_widget()
        # print(self.data)
    def create_widget(self):
        for widget in self.config_frame.winfo_children():
            widget.destroy()
        for index, (solution, time, cycle) in enumerate(zip(self.data["solution"], self.data["time"], self.data["cycle"])):
            self.entry_solution = ctk.CTkEntry(self.config_frame)
            self.entry_solution.grid(row=index, column=0, padx=5, pady=5)
            self.entry_solution.insert(index=0, string=solution)

            self.entry_time = ctk.CTkEntry(self.config_frame)
            self.entry_time.grid(row=index, column=1, padx=5, pady=5)
            self.entry_time.insert(index=0, string=time)

            self.entry_cycle = ctk.CTkEntry(self.config_frame)
            self.entry_cycle.grid(row=index, column=2, padx=5, pady=5)
            self.entry_cycle.insert(index=0, string=cycle)

            self.entry_data.append((self.entry_solution, self.entry_time, self.entry_cycle))
    
    def save_manual_event(self):
        pass

    def rack_amount(self):
        pass

    def clear_event(self):
        pass

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