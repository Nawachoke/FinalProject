# Don't forget to create venv

import tkinter
import tkinter.messagebox
from typing import Optional, Tuple, Union
import customtkinter as ctk
import json
# import ImageProcessing.ImgProc2 as IP
import pandas as pd
import numpy as np
from CTkTable import *

ctk.set_appearance_mode("System") # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("green") # Themes: "blue" (standard), "green", "dark-blue"

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

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10)

        yes_button = ctk.CTkButton(button_frame, text="Yes", command=lambda: self.button_click(True))
        yes_button.pack(side="left", padx=10)

        no_button = ctk.CTkButton(button_frame, text="No", command=lambda: self.button_click(False))
        no_button.pack(side = "right", padx=10)

    def button_click(self, button):
        self.button_clicked = button
        self.destroy()

    def get_result(self):
        if self.focus:
            self.grab_set()
        self.wait_window()
        return self.button_clicked

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.mode_data = None
        self.hours, self.minutes, self.seconds = 0,0,0
        self.running = False
        self.time_indexer = 0
        self.time_counter = 0
        self.pause_count = True

        # self.label = ctk.CTkLabel 

        # set main frame
        self.title("Cell staining machine")
        self.iconbitmap('C:/Project/seniorProject/mainProgram/Bot.ico')
        self.frame = ctk.CTkFrame(self)
        # self.frame.geometry("1080x600")
        self.frame.pack()
        
        # create control frame and widgets
        self.control_center_frame = ctk.CTkFrame(self.frame, corner_radius=0)
        self.control_center_frame.grid(row=0, column=0, sticky="nsew")
        self.control_center_label = ctk.CTkLabel(self.control_center_frame,justify='center', text="Control center", font=('Arial', 24, 'bold'))
        self.control_center_label.grid(row=0, column=0, padx=20, pady=20)

        self.mode_slc = ctk.CTkOptionMenu(self.control_center_frame,
                                                    values= ["1","2","Manual"], font=('Arial', 16), anchor="n")
        self.mode_slc.grid(row=1, column=0, padx=20, pady=20)
        self.start_button = ctk.CTkButton(self.control_center_frame,text= "start", command= self.start_event, font=('Arial', 16, 'bold'))
        self.start_button.grid(row=2, column=0, padx =20, pady=20)
        self.stop_button = ctk.CTkButton(self.control_center_frame, text= "stop", command=self.stop_event, font=('Arial', 16, 'bold'))
        self.stop_button.grid(row=3, column=0, padx =20, pady=20)
        self.pause_button = ctk.CTkButton(self.control_center_frame, text= "pause", command=self.pause_event, font=('Arial', 16, 'bold'))
        self.pause_button.grid(row=4, column=0, padx= 20, pady=20)
        self.image_button = ctk.CTkButton(self.control_center_frame, text= "image", command=self.image_event, font=('Arial', 16, 'bold'))
        self.image_button.grid(row=5, column=0, padx= 20, pady=20)
        self.appearance_mode_option = ctk.CTkOptionMenu(self.control_center_frame, values=["Light", "Dark", "System"],
                                                                  command = self.change_appearance_event, anchor="n")
        self.appearance_mode_option.grid(row =6, column = 0, padx=20, pady=20, sticky="nsew")
        # self.control_center_frame.grid_rowconfigure(0, weight=0)

        # create monitoring frame and widgets
        self.monitor_frame = ctk.CTkFrame(self.frame, width=400, corner_radius=0)
        self.monitor_frame.grid(row=0, column=1, sticky="nsew")
        self.monitor_label = ctk.CTkLabel(self.monitor_frame, justify='center', text="Status monitor", font=('Arial', 24, 'bold'))
        self.monitor_label.grid(row=0, column=0, columnspan= 2)

        self.Protocol_label = ctk.CTkLabel(self.monitor_frame, text="Protocol : ", font=('Arial', 16, 'bold'))
        self.Status_time_label = ctk.CTkLabel(self.monitor_frame, text="Status time : ", font=('Arial', 16, 'bold'))
        self.Current_solution_label = ctk.CTkLabel(self.monitor_frame, text="Current solution : ", font=('Arial', 16, 'bold'))
        self.Next_solution_label = ctk.CTkLabel(self.monitor_frame, text ="Next solution : ", font=('Arial', 16, 'bold'))
        self.Left_rack_label = ctk.CTkLabel(self.monitor_frame, text="Left rack : ", font=('Arial', 16, 'bold'))

        mf = 0
        for status_widget in self.monitor_frame.winfo_children() : 
            status_widget.grid_configure(row=mf, column=0, sticky = "w", padx=20, pady=20)
            mf+=1

        # #Create monitoring data box
        self.Status_time_data = ctk.CTkLabel(self.monitor_frame, text= "", anchor="w", font=('Arial', 16, 'bold'))
        self.Status_time_data.grid(row = 2, column=1, sticky = "w", padx=20, pady=20)
        self.Current_solution_data = ctk.CTkLabel(self.monitor_frame, text="", anchor="w", font=('Arial', 16, 'bold'))
        self.Current_solution_data.grid(row = 3, column = 1 , sticky="w", padx=20, pady=20)
        self.Next_solution_data = ctk.CTkLabel(self.monitor_frame, text= "", anchor="w", font=('Arial', 16, 'bold'))
        self.Next_solution_data.grid(row=4, column=1, sticky = 'w', padx=20, pady=20)
        self.Left_rack_data = ctk.CTkLabel(self.monitor_frame, text="", anchor="w", font=('Arial', 16, 'bold'))
        self.Left_rack_data.grid(row=5, column=1, sticky="w", padx=20, pady=20)

        #set default value
        self.mode_slc.set('MODE')
        self.appearance_mode_option.set('System')

        # set function
    def start_event(self):

        mode = self.mode_slc.get()
        if mode == "1":
            conf_text = "Are you sure starting H & E mode"
        elif mode == "2":
            conf_text = "Are you sure starting in IHC mode"
        else:
            conf_text = "Are you sure starting in manual mode"

        Start_confirm = askyesno(message=conf_text, focus=True)
        answer = Start_confirm.get_result()

        if answer == True and (mode != "1" and mode != "2"):
            self.Manual_window()
        elif answer == True and (mode == "1" or mode == "2"):
            self.mode_data = self.Read_mode(mode)

            self.Protocol_data = ctk.CTkLabel(self.monitor_frame, text=self.mode_data, anchor="w", justify="left", font=('Arial', 16, 'bold'))
            self.Protocol_data.grid(row=1, column=1, padx=10, pady=5, sticky="w")

            #create table
            RawValue = [self.monitoring_data['solution'],
                        self.monitoring_data['time'],
                        self.monitoring_data['cycle']]
            name_list = ['solution', 'time', 'cycle']
            pivoted_value = list(map(list, zip(*RawValue)))
            pivoted_value.insert(0, name_list)

            self.Main_table_frame = ctk.CTkFrame(self.frame)
            self.Main_table_frame.grid(row=0, column=2, padx=20, pady=20)
            # print(self.monitoring_data['cycle'].shape[0])
            self.CycleArray = np.zeros(self.monitoring_data['cycle'].shape[0])
            self.table = CTkTable(master=self.Main_table_frame, values=pivoted_value, font=('Arial', 16))
            self.table.pack(expand=True, fill="both", padx = 20, pady =20)
            self.start_timer()

    def StopMachine(self):
        self.reset_timer()
        print("machine stopped")
        self.time_counter = 0
        self.time_indexer = 0
        self.DataOverwrite()

    def stop_event(self):
        StopConfirm = askyesno(message='Force stop?', focus=True)
        answer = StopConfirm.get_result()
        if answer == True:
            self.StopMachine()

    def pause_event(self):
        if self.pause_count :
            self.pause_button.configure(text="continue")
            self.pause_timer()
            self.pause_count = False
        else:
            self.pause_button.configure(text="pause")
            self.start_timer()
            self.pause_count = True

        # print(self.pause_button.getvar())

    def image_event(self):
        IP.Show_final_image()
        coord = IP.Get_MidPoints()
        print(coord)
        print("Image shown")

    def DataOverwrite(self):
        mode = self.mode_slc.get()
        self.All_mode_data['mode '+str(mode)]['cycle'] = self.CycleArray
        self.All_mode_data = self.All_mode_data.to_json("C:/Project/SeniorProject/mainProgram/mode_conf.json")
        
    def manual_window(self):
        pass

    def Read_mode(self, mode):
        file = open("C:/Project/seniorProject/mainProgram/mode_conf.json")
        data = json.load(file)
        name = data['mode ' + str(mode)]['name']
        step = data['mode ' + str(mode)]['step']
        # solution

        self.All_mode_data = pd.read_json("C:/Project/seniorProject/mainProgram/mode_conf.json")

        self.monitoring_data = pd.DataFrame({  'solution'  : self.All_mode_data['mode ' + str(mode)]['solution'],
                                                'time'     : self.All_mode_data['mode ' + str(mode)]['time'],
                                                'cycle'    : self.All_mode_data['mode ' + str(mode)]['cycle']})

        return name
    
    def change_appearance_event(self, new_appearance_mode : str):
        ctk.set_appearance_mode(new_appearance_mode)

    def start_timer(self):
        if not self.running:
            self.Status_time_data.after(1000)
            self.update()
            self.running = True
    
    def pause_timer(self):
        if self.running:
            self.Status_time_data.after_cancel(self.update_time)
            self.running = False
    
    def reset_timer(self):
        if self.running:
            self.Status_time_data.after_cancel(self.update_time)
            self.running = False

        self.hours, self.minutes, self.seconds = 0,0,0
        self.Status_time_data.configure(text = '00:00:00')
    
    def update(self):
        self.time_counter += 1
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
        self.Status_time_data.configure(text=hours_string + ':' + minutes_string + ':' + seconds_string)
        self.update_time = self.Status_time_data.after(1000, self.update)
        # print(self.time_counter)
        self.CheckState()

    def CheckState(self):
        try:
            if self.time_counter <= self.monitoring_data['time'][self.time_indexer]:
                self.table.deselect_row(self.time_indexer)
                self.Current_solution_data.configure(text= self.monitoring_data['solution'][self.time_indexer])
                self.Next_solution_data.configure(text = self.monitoring_data['solution'][self.time_indexer +1])
                self.Left_rack_data.configure(text = str(len(self.monitoring_data['solution']) - self.time_indexer) + ' rack(s)')
                self.table.select_row(self.time_indexer+1)

            if self.time_counter == self.monitoring_data['time'][self.time_indexer]:
                self.CycleArray[self.time_indexer] += 1
                # print(self.CycleArray)
                # print(self.monitor_frame.winfo_geometry())
                self.time_indexer += 1
                self.time_counter = 0
        except:
            self.StopMachine()
        # print(len(self.monitoring_data['solution']) - self.time_indexer, 'left')
        # print('index',self.time_indexer,'counter',self.time_counter,'second',self.seconds, self.monitoring_data['solution'][self.time_indexer])

if __name__ == "__main__":
    app = App()
    app.mainloop()