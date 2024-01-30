import serial
import struct
import numpy as np 
import time

class Comms():
    def __init__(self):
        
        self.pose_counter = 0
        self.ser = serial.Serial('COM4', 9600)

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
        print(response)

    def SendPoint(self):
        point = self.data[self.pose_counter][:]
        str_point = f"{point[0]},{point[1]},{point[2]}\n"
        self.ser.write(str_point.encode())
        print(f"sending : {point}")