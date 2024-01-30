import tkinter
import numpy as np
import threading as td
import time
from tkinter import Tk, ttk, END, Toplevel
import struct
import serial
import random
import threading

class App(Tk):
    def __init__(self, screenName: str | None = None, baseName: str | None = None, className: str = "Tk", useTk: bool = True, sync: bool = False, use: str | None = None) -> None:
        super().__init__(screenName, baseName, className, useTk, sync, use)
        # self.Main_frame = tkinter.Label
        self.pose_counter = 0
        

        self.data = [(random.randint(0,100), random.randint(0,100), random.randint(1,10)) for _ in range(18)]
        self.ser = serial.Serial('COM4', 9600)
        time.sleep(2)

        self.title("Serial logging")
        #Frames
        self.Main_frame = tkinter.Frame(self)
        self.Main_frame.pack()
        
        self.Control = tkinter.LabelFrame(self.Main_frame, text="Control center", relief="raised", font=('Arial, 16'))
        self.Control.grid(row=0, column=0, padx=20, pady=20, sticky='n')

        #widgets
        self.mode = ttk.Combobox(self.Control, values=["1", "2"])
        self.mode.insert(END, "mode")
        self.mode.grid(row=0, columnspan=2, padx=20, pady=20, sticky='news')
        self.mode.grid_anchor('n')
        self.Whole_pack = tkinter.Button(self.Control, text="ALL",command= self.Whole_pack, width=10, height=6, font=('Arial, 16'))
        self.Whole_pack.grid(row=1, column=0, padx=20, pady=20, sticky='news')
        self.One_point = tkinter.Button(self.Control,command=self.One_point, text="ONE", width=10, height=6, font=('Arial, 16'))
        self.One_point.grid(row=1, column=1, padx=20, pady=20, sticky='news')
        self.Stop = tkinter.Button(self.Control,command=self.Stop, text='close port',width=10, height=6, font=('Arial, 16'))
        self.Stop.grid(row=2, column=1, padx=20, pady=20, sticky='news')
        self.ShowData = tkinter.Button(self.Control, command=self.ShowData,width=10, height=6, font=('Arial, 16'), text='Raw data')
        self.ShowData.grid(row=2, column=0, padx=20, pady=20, sticky='news')
        print(len(self.data), self.data)
        thread1 = threading.Thread(target=self.receive_response)
        thread1.start()

    def receive_response(self):
        i=1
        try:
            while True:
                if self.ser.in_waiting > 0:
                    response  = self.ser.readline().decode().strip()
                    print(f"response : {response}, iteration : {i}")
                    i+=1
        except KeyboardInterrupt:
            pass
        finally:
            self.ser.close()
    
    def ShowData(self):
        print(self.data)

    def Stop(self):
        time.sleep(0.5)
        self.ser.close()

    def Whole_pack(self):
        try :
            for i in range(len(self.data)):
                point = self.data[i][:]
                str_point = f"{point[0]},{point[1]},{point[2]}\n"
                self.ser.write(str_point.encode())
                print(f"sending : {point}")
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally :
            self.ser.close()
        time.sleep(1)
        
    def One_point(self):
        point = self.data[self.pose_counter][:]
        str_point = f"{point[0]},{point[1]},{point[2]}\n"
        self.ser.write(str_point.encode())
        print(f"sending : {point}")
   
if  __name__ == '__main__':

    App = App()
    App.mainloop()