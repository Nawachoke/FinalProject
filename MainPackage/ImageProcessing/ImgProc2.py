import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# global final_image, mid_points

def Read_image():
    img = cv2.imread('C:/Project/test_image3.png')
    return img

def Get_real_image():
    img_copy = Read_image()    
    return img_copy

def Show_real_image():
    img = Get_real_image()
    img = cv2.resize(img, (450, 450))
    plt.title('Original Image')
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.xticks([])
    plt.yticks([])
    plt.show()

def HSV_th():
    hsv = cv2.cvtColor(Get_real_image(), cv2.COLOR_BGR2HSV)
    # lower = np.array([88,  72,  140])
    # upper = np.array([225, 143, 255])
    lower = np.array([93,   144,   119])
    upper = np.array([115, 170, 255])
    mask = cv2.inRange(hsv, lower, upper)
    # plt.figure('image')
    # plt.imshow(cv2.cvtColor(mask, cv2.COLOR_BGR2RGB))
    return mask

def Get_binary():
    img = HSV_th()
    cv2.imwrite('binary_image.png', img)
    return img

def Contouring():
    bin_im = HSV_th()
    ctrs, hier = cv2.findContours(bin_im, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    ctrd = cv2.drawContours(Get_real_image(), ctrs, -1, (0,0,255), 2)
    return ctrd

def Findpeaks():

    def SumRow():
        img = HSV_th()
        rows = np.vsplit(img, np.shape(img)[0])
        sumall = []
        for r in rows:
            sumall.append(r.sum())
        return sumall
    
    def SumCol():
        img = HSV_th()
        cols = np.hsplit(img, np.shape(img)[1])
        sumall = []
        for c in cols:
            sumall.append(c.sum())
        return sumall
    
    def CalPeaks(Sumval, d):
        peaks, _ = find_peaks(Sumval, distance=d)
        return peaks
    
    def find_mean(arr) -> list:
        mean = np.mean(arr)
        mean_list = [mean for i in range(len(arr))]
        return mean_list

    peakr = CalPeaks(SumRow(), 80)
    peakc = CalPeaks(SumCol(), 50)

    data = [SumRow(), SumCol()]
    plt.figure('values')
    titles = ['peak row', 'peak col']
    mean_data = [find_mean(SumRow()), find_mean(SumCol())]
    
    for i in range(len(titles)):
       plt.subplot(1, 2, i+1)
       plt.title(titles[i])
       plt.plot(data[i]) #plot sum
       plt.plot(mean_data[i]) #plot mean data
    plt.show()
    return  peakr, peakc

def DrawCross():
    img = Get_real_image()
    Y,X = Findpeaks()
    for r in range(len(Y)):
        for c in range(len(X)):
            
            img = cv2.circle(img, (X[c], Y[r]), radius=4, color=(0,0,255), thickness=-1)

    return img

def Get_Corner():
    Y, X = Findpeaks()
    coord = []
    for r in range(len(Y)):
        for c in range(len(X)):
            coord.append([X[c], Y[r]])
    return coord

def DrawCenter():
    global final_image
    final_image = DrawCross()
    Y,X = Findpeaks()
    def Cal_center(arr):
        coord = []
        for i in range(1, len(arr)):
            coord.append(np.round_((arr[i] + arr[i-1])/2))
        return coord
    mid_X = Cal_center(X)
    mid_Y = Cal_center(Y)
    coords = []
    for r in range(len(mid_Y)):
        for c in range(len(mid_X)):
            final_image = cv2.circle(final_image, (int(mid_X[c]), int(mid_Y[r])), radius=4, color=(0, 255, 255), thickness=-1)
            coords.append([mid_X[c], mid_Y[r]])
    
    return final_image, coords

def Get_MidPoints():
    _, coords = DrawCenter()
    return coords

def put_number():
    img, points = DrawCenter()
    amt = len(points)
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 1
    color = (0, 0, 0)
    thickness = 2
    for i in range(amt):
        x=points[i][0]
        y=points[i][1]
        img = cv2.putText(img, str(i+1), (int(x),int(y)), font, fontScale, color, thickness)
        
    return img
    
def Show_final_image():
    image = put_number()
    plt.title('Captured image')
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.xticks([])
    plt.yticks([])
    plt.show()
    cv2.imwrite('final_image.png', image)
