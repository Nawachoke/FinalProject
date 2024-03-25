import tkinter
from typing import Optional, Tuple, Union
import customtkinter as ctk
import sys
import json
# from ImageProcessing import TrayFinder3
import ImageProcessing.TrayFinder3 as TF
import pandas as pd
import numpy as np
from CTkTable import *
import threading
import time
import os
from PIL import Image
# from manualw import ManualWindow
# from SerialComms import Comms
import random
import serial

ctk.set_appearance_mode("System") # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue") # Themes: "blue" (standard), "green", "dark-blue"

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
        self.MainFrame.pack(pady=10, padx=10)
        self.label = ctk.CTkLabel(self, text="Please select mode configuration.")
        self.label.pack(side='top',pady=10, padx=10)

        self.new_protocol_button = ctk.CTkButton(self.MainFrame, text="New")
        self.new_protocol_button.pack(side='right', padx=10, pady=10)
        self.protocol_adjust_button = ctk.CTkButton(self.MainFrame, text="Adjust")
        self.protocol_adjust_button.pack(side='left', padx=10, pady=10)

    def adjust_event(self):
        pass
    
    def new_prot_event(self):
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

        self.warn_image = ctk.CTkImage(Image.open("MainPackage\image\warning-sign.png"), size=(50,50))
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
        # self.data = [(random.randint(0,100), random.randint(0,100), random.randint(1,10)) for _ in range(18)]
        
        self.ser = serial.Serial('COM3', 9600)
        self.iterator = 0
        self.running = False
        self.hours, self.minutes, self.seconds = 0,0,0
        self.progress_val = 0.0
        
        self.data_points = [(random.randint(0, 100), random.randint(0, 100), random.randint(1, 10)) for _ in range(18)]

        self.iconbitmap("MainPackage\image\icons8-cell-50.ico")
        self.response = None

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
        self.mode_optionmenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["IHC", "H&E", "settings"], command=self.mode_event)
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
        self.progress_bar_frame.grid(row=3, column = 1, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.progress_bar_label = ctk.CTkLabel(self.progress_bar_frame, text="Progression :")
        self.progress_bar_label.grid(row=0, column=0, padx=10, pady=(10, 10))
        self.progress_bar = ctk.CTkProgressBar(self.progress_bar_frame, progress_color="green", width=700)
        self.progress_bar.grid(row=0, column=1, columnspan=6, padx=10, pady=10, sticky="nsew")
        self.percentage_label = ctk.CTkLabel(self.progress_bar_frame, text=f"{self.progress_val * 100} / 100%")
        self.percentage_label.grid(row=0, column=8, sticky='e')

        #Monitoring frame
        self.monitoring_frame = ctk.CTkFrame(self, width=100, corner_radius=20)
        self.monitoring_frame.grid(row=0, column=1, padx=20, pady=20, rowspan=2, sticky="nsew")
        self.monitor_label = ctk.CTkLabel(self.monitoring_frame, text="Status monitor", font=ctk.CTkFont(size=24, weight="bold"))
        self.monitor_label.grid(row=0, column=0, sticky="news")

        self.Protocol_label = ctk.CTkLabel(self.monitoring_frame, text="Protocol : ", font=('Arial', 16, 'bold'))
        self.Run_time_label = ctk.CTkLabel(self.monitoring_frame, text="Run time : ", font=('Arial', 16, 'bold'))
        self.Current_solution_label = ctk.CTkLabel(self.monitoring_frame, text="Current solution : ", font=('Arial', 16, 'bold'))
        self.Next_solution_label = ctk.CTkLabel(self.monitoring_frame, text ="Next solution : ", font=('Arial', 16, 'bold'))
        self.Left_rack_label = ctk.CTkLabel(self.monitoring_frame, text="Left rack : ", font=('Arial', 16, 'bold'))
        mf = 0
        for status_widget in self.monitoring_frame.winfo_children() : 
            status_widget.grid_configure(row=mf, column=0, sticky = "w", padx=20, pady=20)
            mf+=1
        
        self.Protocol_data = ctk.CTkLabel(self.monitoring_frame, text="", anchor="w", justify="left", font=('Arial', 16, 'bold'))
        self.Protocol_data.grid(row=1, column=1, padx=20, pady=20, sticky="w")
        self.Run_time_data = ctk.CTkLabel(self.monitoring_frame, text= "", anchor="w", font=('Arial', 16, 'bold'))
        self.Run_time_data.grid(row = 2, column=1, sticky = "w", padx=20, pady=20)
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
        thread1 = threading.Thread(target=self.receive_response)
        thread1.start()

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)
    
    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def image_event(self):
        self.data = TF.TrayFinder("raw_image.png")
        self.data.Undistorted(self.data.image)
        self.data_points = self.data.FindMidpoint()
        self.data.ShowImage('result', self.data.contoured_image)
        print(type(self.data_points[0][0]))
    
    def start_event(self):
        Start_confirm = askyesno(message='Start machine?', focus=True)
        answer = Start_confirm.get_result()
        data_pack = {"x": 0, "y": 0, "t": 0}
        if answer:
            self.Run_time_data.configure(text = '00:00:00')
            self.start_timer()
            self.send_package(command="position", data_list=data_pack)

    def stop_event(self):
        Stop_confirm = askyesno(message="Stop machine?", focus=True)
        answer = Stop_confirm.get_result()
        if answer:
            self.send_package(command="stop")

    def pause_event(self):
        Pause_confirm = askyesno(message="Pause_machine?", focus=True)
        answer = Pause_confirm.get_result()
        if answer:
            self.send_package(command="pause")

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
            self.Confirm(message, mode_number)
        elif mode == "IHC":
            message = "Start with IHC mode"
            mode_number = 2
            self.Confirm(message, mode_number)
        elif mode == "settings":
            message = "Config Protocol"
            mode_config = ManualWindow()
        else:
            pass

    def Confirm(self, message, mode_number=None):
        Mode_confirm = askyesno(message=message, focus=True)
        answer = Mode_confirm.get_result()

        if answer == True and mode_number >= 1:
            self.mode_name = self.Read_Data(mode_number)
            self.Protocol_data.configure(text=self.mode_name)
            self.iterator = 0
            self.DestroyTable()
            self.show_table()
            self.Status_update()
        
        # elif answer == True:
        #     mod

    def DestroyTable(self):
        for widget in self.Table_frame.winfo_children() :
            widget.destroy()
    
    def Read_Data(self, mode_number):
        file = open("C:/Project/FinalProject/MainPackage/mode_conf.json")
        data = json.load(file)
        mode_name = data['mode ' + str(mode_number)]['name']
        self.Mode_data = pd.read_json("C:/Project/FinalProject/MainPackage/mode_conf.json")
        self.monitoring_data = pd.DataFrame({  'solution'  : self.Mode_data['mode ' + str(mode_number)]['solution'],
                                                'time'     : self.Mode_data['mode ' + str(mode_number)]['time'],
                                                'cycle'    : self.Mode_data['mode ' + str(mode_number)]['cycle']})
        return mode_name

    def DataOverwrite(self):
        pass
    
    #communication thread
    def receive_response(self):
        data_pack = {"x": 0, "y": 0, "t": 0}
        try:
            while True:
                if self.ser.in_waiting > 0:
                    self.response = self.ser.readline().decode('utf-8').strip()
                    print(f"response : {self.response}")
                    if self.response == "request" and self.iterator != len(self.data_points):
                        # print(self.iterator)
                        data_pack.update({"x":self.data_points[self.iterator][0], "y":self.data_points[self.iterator][1], "t":self.monitoring_data['time'][self.iterator]})
                        self.send_package("position", data_list=data_pack)
                        time.sleep(0.5)
                        self.iterator += 1
                        self.Status_update()
        except Exception as e:
            print(f"Error in receive_response: {e}")
        except KeyboardInterrupt:
            pass

    def send_package(self, command, data_list=None):
        package = {"command": command, "data": data_list}
        json_data = json.dumps(package)
        self.ser.write((json_data + '\n').encode('ascii'))
        self.ser.flush()
        print(f"Sent JSON package: {json_data}")

    def Status_update(self):
        self.table.deselect_row(self.iterator)
        self.Current_solution_data.configure(text= self.monitoring_data['solution'][self.iterator])
        self.Next_solution_data.configure(text = self.monitoring_data['solution'][self.iterator +1])
        self.Left_rack_data.configure(text = str(len(self.monitoring_data['solution']) - self.iterator) + ' rack(s)')
        self.table.select_row(self.iterator+1)
        # self.progress_percent = (len(self.monitoring_data['solution']) - self.iterator) / len(self.monitoring_data['solution'])
        self.updateProgressBar()
        print(self.progress_val)

    def updateProgressBar(self):
        self.progress_val = 1 - ((len(self.monitoring_data['solution']) - self.iterator) / len(self.monitoring_data['solution']))
        self.progress_val = round(self.progress_val, 2)
        self.progress_bar.set(self.progress_val)
        self.percentage_label.configure(text=f"{int(self.progress_val * 100)} / 100%")

    #timer function
    def start_timer(self):
        if not self.running:
            self.Run_time_data.after(1000)
            self.update()
            self.running = True
    
    def pause_timer(self):
        if self.running:
            self.Run_time_data.after_cancel(self.update_time)
            self.running = False
    
    def reset_timer(self):
        if self.running:
            self.Run_time_data.after_cancel(self.update_time)
            self.running = False

        self.hours, self.minutes, self.seconds = 0,0,0
        self.Run_time_data.configure(text = '00:00:00')
    
    def update(self):
        # self.time_counter += 1
        self.seconds += 1
        if self.seconds == 60:
            self.minutes += 1
            self.seconds = 0
        if self.minutes == 60:
            self.hours += 1
            self.minutes = 0

        hours_string = f'{self.hours}' if self.hours > 9 else f'0{self.hours}'
        minutes_string = f'{self.minutes}' if self.minutes > 9 else f'0{self.minutes}'
        seconds_string = f'{self.seconds}' if self.seconds > 9 else f'0{self.seconds}'
        self.Run_time_data.configure(text=hours_string + ':' + minutes_string + ':' + seconds_string)
        self.update_time = self.Run_time_data.after(1000, self.update)

if __name__ == "__main__":
    app = App()
    app.mainloop()