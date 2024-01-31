import serial
import json
import time
import threading
import random
import tkinter as tk

class App(tk.Tk):
    def __init__(self, screenName=None, baseName=None, className="Tk", useTk=True, sync=False, use=None) -> None:
        super().__init__(screenName, baseName, className, useTk, sync, use)

        self.data = [(random.randint(0, 100), random.randint(0, 100), random.randint(1, 10)) for _ in range(18)]
        self.ser = serial.Serial('COM3', 9600, timeout=3)
        self.iterator = 0
        time.sleep(2)

        # Main frame
        self.title("Serial logging")
        self.Main_frame = tk.Frame(self)
        self.Main_frame.pack()

        self.Control_panel = tk.LabelFrame(self.Main_frame, text="Control center", relief="raised", font=('Arial'))
        self.Control_panel.grid(row=0, column=0, padx=20, pady=20, sticky='n')

        self.Start_button = tk.Button(self.Control_panel, text='START', command=self.start_event)
        self.Start_button.grid(row=0, column=0, padx=20, pady=20)
        self.Stop_button = tk.Button(self.Control_panel, text='STOP', command=self.stop_event)
        self.Stop_button.grid(row=0, column=1, padx=20, pady=20)
        self.Pause_button = tk.Button(self.Control_panel, text='PAUSE', command=self.pause_event)
        self.Pause_button.grid(row=1, column=0, padx=20, pady=20)
        self.Continue_button = tk.Button(self.Control_panel, text='CONTINUE', command=self.continue_event)
        self.Continue_button.grid(row=1, column=1, padx=20, pady=20)

        thread1 = threading.Thread(target=self.receive_response)
        thread1.start()

    def start_event(self):
        print(self.data)
        data_pack = {"x": 0, "y": 0, "t": 0}
        self.send_package("position", data_list=data_pack)

    def receive_response(self):
        data_pack = {"x": 0, "y": 0, "t": 0}
        try:
            while True:
                if self.ser.in_waiting > 0:
                    self.response = self.ser.readline().decode('utf-8').strip()
                    print(f"response : {self.response}")
                    if self.response == "request" and self.iterator != len(self.data):
                        print(self.iterator)
                        data_pack.update({"x":self.data[self.iterator][0], "y":self.data[self.iterator][1], "t":self.data[self.iterator][2]})
                        self.send_package("position", data_list=data_pack)
                        self.iterator += 1
        except Exception as e:
            print(f"Error in receive_response: {e}")
        except KeyboardInterrupt:
            pass

    def stop_event(self):
        self.ser.flush()
        self.send_package(command="stop")

    def pause_event(self):
        self.send_package(command="pause")

    def continue_event(self):
        pass

    def send_package(self, command, data_list=None):
        package = {"command": command, "data": data_list}
        json_data = json.dumps(package)
        self.ser.write((json_data + '\n').encode('ascii'))
        self.ser.flush()
        print(f"Sent JSON package: {json_data}")
        

if __name__ == '__main__':
    app = App()
    app.mainloop()
