import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

class TrayFinder:
    def __init__(self, file_path=None):
        if file_path != None:
            self.image = cv2.imread(str(file_path))
        else:
            self.image = self.capture_image()
        self.blur = None
        self.gray = None
        self.mask = None
        self.morph = None
        self.contoured_image = None
        self.merr = None
    
    #Image processing
    def HSV_threshold(self):
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        self.blur = cv2.GaussianBlur(self.gray, (3,3), 0)
        lower = np.array([61,   105,  202])
        upper = np.array([108,  255, 255])
        self.mask = cv2.inRange(self.blur, lower, upper)
        return self.mask

    def Contouring(self):
        masked = self.HSV_threshold()
        kernel = np.ones((3,3), np.uint8)
        # self.morph = cv2.erode(masked, kernel, iterations=1)
        # self.morph = cv2.morphologyEx(masked, cv2.MORPH_OPEN, kernel, iterations=1)
        ctrs, hier = cv2.findContours(masked, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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

        self.merr, aerr = self.point_filtering(areas, midpoint)

        for i in range(len(self.merr)):
            cv2.putText(self.contoured_image, str(i+1), (self.merr[i] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.circle(self.contoured_image, (self.merr[i]), radius=2, color=(255, 255, 255), thickness=-1)
            # cv2.putText(self.contoured_image, str(merr[i]), (merr[i]), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 2

    def point_filtering(self, areas, midpoint):
        areas = np.array(areas)
        midpoint = np.array(midpoint)
        # print(areas)
        # print(midpoint)
        # print('area filtering')
        AreaMean = np.mean(areas[areas!=0])
        SF = np.mean(areas[areas!=0])*0.15 #Safety Factor
        # print(AreaMean, AreaMean+SF, AreaMean-SF)
        aerr, merr = [], []
        for i in range(len(areas)):
            if areas[i] < (AreaMean + SF) and areas[i] > (AreaMean - SF):
                # print(i, areas[i], midpoint[i])
                aerr.append(i)
                merr.append(midpoint[i])

        return merr, aerr

    def sort_point(self, points):
        sum_value = [sum(point) for point in points]
        sorted_value = [val for _, val in sorted(zip(sum_value, points), reverse=True)]
        # for i in range(len(sorted_value)):
        #     print(points[i], sum_value[i], sorted_value[i], i+1)
        return sorted_value
            
    def export_points(self, points, name):
        data = pd.DataFrame(points)
        data.to_csv(name, index=False)

    def ShowImage(self, window_name, image):
        plt.title(window_name)
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.show()

    def Get_Binary(self):
        return self.morph
    
    def Save_Image(self, file_name, image):
        cv2.imwrite(file_name, image)

    # def show(self):
    #     print(self.file_path)
    def capture_image(self):
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Unable to open camera.")
            return
        
        ret, frame = cap.read()

        if not ret:
            print("Error Unable to capture frame")
            cap.release()
            return None
        
        cap.release()

        return frame

if __name__ == '__main__':
    tray_finder = TrayFinder()
    tray_finder.ShowImage('raw image', image=tray_finder.image)
    tray_finder.FindMidpoint()
    tray_finder.ShowImage('midpoints', image=tray_finder.contoured_image)
    tray_finder.Save_Image('result.png', image=tray_finder.contoured_image)
    tray_finder.export_point(points= tray_finder.merr, name='points.csv')
