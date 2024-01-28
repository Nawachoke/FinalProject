import matplotlib.pyplot as plt
import cv2
import numpy as np
import imutils
import glob

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
        lower = np.array([0,   137,  163])
        upper = np.array([255,  228, 239])
        self.mask = cv2.inRange(self.blur, lower, upper)
        return self.mask

    def Contouring(self):
        masked = self.HSV_threshold()
        kernel = np.ones((3,3), np.uint8)
        # self.morph = cv2.erode(masked, kernel, iterations=1)
        # self.morph = cv2.morphologyEx(masked, cv2.MORPH_OPEN, kernel, iterations=1)
        ctrs, hier = cv2.findContours(self.mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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
            # print(f'Area of contour {i+1}:', area)
        areas = np.array(areas)
        midpoint = np.array(midpoint)
        # print(areas)
        # print(midpoint)
        # print(np.mean(areas), np.mean(areas) + np.mean(areas)*0.05)
        # aerr = []
        # for i in range(len(areas)):
        #     if areas[i] < (np.mean(areas) + (np.mean(areas)*0.2)):
        #         print(i)
        #         aerr.append(i)
        # filter_areas = [value for index, value in enumerate(areas) if index not in aerr]
        # print(filter_areas)
        # filter_midpoint = [value for index, value in enumerate(midpoint) if index not in aerr]
        # print(filter_midpoint)
        # midpoint.sort(axis=0)
        for i in range(len(midpoint)):
                cv2.putText(self.contoured_image, str(i+1),(midpoint[i]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.circle(self.contoured_image, (midpoint[i]), radius=2, color=(255, 255, 255), thickness=-1)
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
    # Find = TrayFinder(file_path='C:/Project/FinalProject/Images/test_image_cam_jig2_0.png')
    # mid_points = Find.FindMidpoint()
    # mid_points.sort(axis=1)
    # print(mid_points)
    # Find.FindMidpoint()
    # Find.ShowImage('midpoints', Find.contoured_image)
    # Find.ShowImage('blur', Find.morph)
    paths = glob.glob("C:/Project/FinalProject/MainPackage/ImageProcessing/Images/*.png")
    count = 0
    for file_path in paths[:12]:
        count += 1
        tray_finder = TrayFinder(file_path)
        tray_finder.FindMidpoint()
        tray_finder.ShowImage(f'midpoint{count}', tray_finder.contoured_image)
        tray_finder.ShowImage(f'gray{count}', tray_finder.morph)

