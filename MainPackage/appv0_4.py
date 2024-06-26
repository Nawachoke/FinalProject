import tkinter
from typing import Optional, Tuple, Union
import customtkinter as ctk
import sys
import json
import ImageProcessing.TrayFinder3 as TF
import pandas as pd
import numpy as np
from CTkTable import *
import threading
import time
from PIL import Image
import random
import serial
import Manual
import os
import glob
import cv2

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

        self.warn_image = ctk.CTkImage(Image.open("MainPackage/image/warning-sign.png"), size=(50,50))
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
        self.folder = "MainPackage/Protocols"
        files = glob.glob(self.folder+"/*")
        self.file_names = [os.path.splitext(os.path.basename(file))[0] for file in files if file.endswith('.json')]
        # for file_name in self.file_names:
        #     print(file_name)
        self.file_names.append('settings')
        try:
            self.ser = serial.Serial('COM3', 9600)
            print("Serial connection established")
        except serial.SerialException as e:
            print(f"Serial connection error:{e}")
        except Exception as e:
            print(f"Error:{e}")
        self.iterator = 0
        self.running = False
        self.hours, self.minutes, self.seconds = 0,0,0
        self.progress_val = 0.0
        
        # self.data_points = [(random.randint(0, 100), random.randint(0, 100), random.randint(1, 10)) for _ in range(18)]
        # self.data_points = pd.read_csv('MainPackage/ImageProcessing/previous_points.csv')

        self.iconbitmap("MainPackage/image/icons8-cell-50.ico")
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
        self.mode_optionmenu = ctk.CTkOptionMenu(self.sidebar_frame, values=self.file_names, command=self.mode_event)
        self.mode_optionmenu.grid(row=2, column=0, padx=20, pady=10)
        self.image_button = ctk.CTkButton(self.sidebar_frame, text="IMAGE", command=self.image_event, font=ctk.CTkFont(size=16))
        self.image_button.grid(row=3, column=0, padx=20, pady=10)
        self.start_button = ctk.CTkButton(self.sidebar_frame, text="START", command=self.start_event, font=ctk.CTkFont(size=16))
        self.start_button.grid(row = 4, column=0, padx=20, pady=10)
        self.stop_button = ctk.CTkButton(self.sidebar_frame, text="STOP", command=self.stop_event, font=ctk.CTkFont(size=16))
        self.stop_button.grid(row=5, column = 0, padx=20, pady=10)
        self.camera_button = ctk.CTkButton(self.sidebar_frame, text="CAMERA", command=self.camera_event, font=ctk.CTkFont(size=16))
        self.camera_button.grid(row=6, column=0, padx=20, pady=10)
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
        self.appearance_mode_optionmenu.set("System")
        self.scaling_optionmenu.set("100")
        self.mode_optionmenu.set("MODE")
        self.progress_bar.set(0)
        self.thread1 = threading.Thread(target=self.receive_response)
        self.thread1.setDaemon(True)
        self.thread1.start()

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)
    
    def Px2StepX(self, data):
        m2s = 0.2 #mm/step
        Xfactor = 370/268
        Xspace = -130
        converted_data = ((((640 - data) / Xfactor) / m2s) + Xspace)
        return int(converted_data)

    def Px2StepY(self, data):
        m2s = 0.2 #mm/step
        Yfactor = 354/256
        Yspace = 305
        converted_data = ((((480 - data) / Yfactor) / m2s) + Yspace)
        return int(converted_data)
    
    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def image_event(self):
        self.send_package("Homeposition")
        self.data = TF.TrayFinder("raw_image.png")
        self.data.Undistorted(self.data.image)
        self.data_points = self.data.FindMidpoint()
        self.data.ShowImage('result', self.data.contoured_image)
        self.data.export_points(self.data.points, name='MainPackage/ImageProcessing/previous_points.csv')
        print(type(self.data_points[0][0]))
    
    def start_event(self):
        Start_confirm = askyesno(message='Start machine?', focus=True)
        answer = Start_confirm.get_result()
        data_pack = {"x": 0, "y": 0, "t": 0}
        if answer:
            self.Run_time_data.configure(text = '00:00:00')
            self.start_timer()
            self.send_package(command="Homestart", data_list=data_pack)
            self.iterator = 0

    def stop_event(self):
        Stop_confirm = askyesno(message="Stop machine?", focus=True)
        answer = Stop_confirm.get_result()
        if answer:
            self.send_package(command="stop")
            self.DataOverwrite()

    def camera_event(self):
        Pause_confirm = askyesno(message="Monitor real time video?", focus=True)
        answer = Pause_confirm.get_result()
        if answer:
            # self.send_package(command="pause")
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("Error : Unable to open camera.")
            while(True):
                ret, frame = cap.read()
                cv2.imshow("Press Q to exit!", frame)
                if cv2.waitKey(1) and 0xFF == ord('q'):
                    
                    break
                cap.release()
                cv2.destroyAllWindows()

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
        if mode != 'settings':
            message = 'Start with '+mode+' mode'
            self.Confirm(message)
        else : 
            manual_configuration_window = Manual.ManualWindow()

    def Confirm(self, message, mode_number=None):
        Mode_confirm = askyesno(message=message, focus=True)
        answer = Mode_confirm.get_result()

        if answer == True:
            self.Read_Data(self.mode)
            self.Protocol_data.configure(text=self.mode)
            self.iterator = 0
            self.DestroyTable()
            self.show_table()
            self.Status_update()

    def Read_Data(self, mode : str):
        self.path = os.path.join(self.folder, mode + '.json')
        file = open(self.path)
        data = json.load(file)
        self.monitoring_data = pd.DataFrame({ 'solution' : data['solution'],
                                              'time'     : data['time'],
                                              'cycle'    : data['cycle']})
        self.cycle_data = np.zeros(self.monitoring_data['cycle'].shape[0])
        
    def DestroyTable(self):
        for widget in self.Table_frame.winfo_children() :
            widget.destroy()
    
    def DataOverwrite(self):
        self.monitoring_data['cycle'] = self.cycle_data
        self.monitoring_data = self.monitoring_data.to_json(self.path)
    
    #communication thread
    def receive_response(self):
        data_pack = {"x": 0, "y": 0, "t": 0}
        while True:
                if self.ser.in_waiting > 0:
                    self.response = self.ser.readline().decode('utf-8').strip()
                    print(f"response : {self.response}")
                    if self.response == "request" and self.iterator != len(self.data_points):
                        data_pack.update({"x": self.Px2StepX(self.data_points[self.iterator][0]), 
                                          "y": self.Px2StepY(self.data_points[self.iterator][1]), 
                                        "t": self.monitoring_data['time'][self.iterator]})
                        self.send_package("position", data_list=data_pack)
                        time.sleep(0.5)  # careful with sleep, it could delay the loop
                        self.cycle_data[self.iterator] += 1
                        self.iterator += 1
                        self.Status_update()
                    elif self.response == 'request' and self.iterator == len(self.monitoring_data['time']):
                        print("Final request received. Stopping")
                        self.FinishTask()

    def send_package(self, command, data_list=None):
        if data_list:
            # Convert all NumPy integers in the data_list to Python integers
            data_list = {k: v.item() if isinstance(v, np.integer) else v for k, v in data_list.items()}

        package = {"command": command, "data": data_list}
        json_data = json.dumps(package)
        self.ser.write((json_data + '/n').encode('ascii'))
        self.ser.flush()
        print(f"Sent JSON package: {json_data}", self.iterator)

    def Status_update(self):
        try: 
            self.table.deselect_row(self.iterator-1)
            self.table.select_row(self.iterator)
            self.Left_rack_data.configure(text = (len(self.monitoring_data['solution']) - self.iterator))
            self.Current_solution_data.configure(text = self.monitoring_data['solution'][self.iterator-1])
            self.Next_solution_data.configure(text = self.monitoring_data['solution'][self.iterator])
        except Exception as e:
            print(f"Error in update data: {e}")

        self.updateProgressBar()

    def updateProgressBar(self):
        self.progress_val = (1 - ((len(self.monitoring_data['solution']) - self.iterator) )/ len(self.monitoring_data['solution']))
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
    
    def FinishTask(self):
        Task_accept =askyesno(message="The task is finished", focus=True)
        answer = Task_accept.get_result()
        self.DataOverwrite()
        if answer:
            time.sleep(0.2)
            self.pause_timer()
            try:
                self.ser.close()
                self.thread1.join()
            except Exception as e:
                print(f"Error message : {e}")
            sys.exit(self)

if __name__ == "__main__":
    app = App()
    app.mainloop()