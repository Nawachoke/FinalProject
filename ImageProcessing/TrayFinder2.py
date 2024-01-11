import matplotlib.pyplot as plt
import cv2
import numpy as np
import imutils

class TrayFinder:
    def __init__(self, file_path):
        self.image = cv2.imread(str(file_path))
        self.blur = None
        self.gray = None
        self.mask = None
        self.morph = None
        self.contoured_image = None
    
    #Image processing
    def HSV_threshold(self):
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        self.blur = cv2.GaussianBlur(self.gray, (3,3), 0)
        lower = np.array([0,   158,  150])
        upper = np.array([255,  255, 255])
        self.mask = cv2.inRange(self.blur, lower, upper)
        return self.mask

    def Contouring(self):
        masked = self.HSV_threshold()
        kernel = np.ones((3,3), np.uint8)
        # self.morph = cv2.erode(masked, kernel, iterations=1)
        self.morph = cv2.morphologyEx(masked, cv2.MORPH_OPEN, kernel, iterations=1)
        ctrs, hier = cv2.findContours(self.morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.contoured_image = cv2.drawContours(self.image, ctrs, -1, (0, 0, 255), 2)

        return ctrs

    def Findpeaks(self):
        masked = self.HSV_threshold()
        rows = np.vsplit(masked, np.shape(masked)[0])
        cols = np.hsplit(masked, np.shape(masked)[1])

    def FindMidpoint(self):
        contour = self.Contouring()
        midpoint = []
        areas = []
        for i, cnt in enumerate(contour):
            M = cv2.moments(cnt)
            if M['m00'] != 0.0:
                x1 = int(M['m10']/M['m00'])
                y1 = int(M['m01']/M['m00'])
            area = cv2.contourArea(cnt)
            midpoint.append([x1, y1])
            areas.append(area)
            print(f'Area of contour {i+1}:', area)
        areas = np.array(areas)
        midpoint = np.array(midpoint)
        # for i in range(len(areas)):
        #     if areas[i] > 
        # if areas[i] >= areas.mean():
        # midpoint.sort(axis=0)
        for i in range(len(midpoint)):
                cv2.putText(self.contoured_image, str(i+1),(midpoint[i]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        print(midpoint)
        print(np.mean(areas), np.median(areas))
    #optional function
    def Copy_image(self):
        pass

    def Show_real_image(self):
        pass

    def ShowImage(self, window_name, image):
        plt.title(window_name)
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        plt.show()

    def Get_Binary(self):
        return self.morph

    # def show(self):
    #     print(self.file_path)

if __name__ == '__main__':
    Find = TrayFinder(file_path='C:/Project/FinalProject/Images/test_image_twinbar_top_2.png')
    # mid_points = Find.FindMidpoint()
    # mid_points.sort(axis=1)
    # print(mid_points)
    Find.FindMidpoint()
    Find.ShowImage('midpoints', Find.contoured_image)
    Find.ShowImage('blur', Find.morph)

