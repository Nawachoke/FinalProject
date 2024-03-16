import matplotlib.pyplot as plt
import cv2
import numpy as np
import imutils
import glob
import pandas as pd
import pickle

class TrayFinder:
    def __init__(self, file_path):
        self.image = cv2.imread(str(file_path))
        self.blur = None
        self.gray = None
        self.mask = None
        self.morph = None
        self.contoured_image = None
        self.merr = None
    
    def Undistorted(self, image):
        with open('MainPackage/ImageProcessing/CalibrationMatrices/cameraMatrix.pkl', 'rb') as f1:
            cameraMatrix = pickle.load(f1)
        
        with open('/MainPackage/ImageProcessing/CalibrationMatrices/dist.pkl', 'rb') as f2:
            dist = pickle.load(f2)
        
        h, w = image.shape[:2]
        newCameraMatrix, roi = cv2.getOptimalNewCameraMatrix(cameraMatrix, dist, (w,h), 1, (w,h))
        #undistort
        dst = cv2.undistort(image, cameraMatrix, dist, None, newCameraMatrix)
        #crop the image
        x, y, w, h = roi
        dst = dst[y:y+h, x:x+w]
        cv2.imwrite('caliResult1.png', dst)

        # mapx, mapy = cv2.initUndistortRectifyMap(cameraMatrix, dist, None, newCameraMatrix, (w,h), 5)
        # dst = cv2.remap(image, mapx, mapy, cv2.INTER_LINEAR)

        # # crop the image
        # x, y, w, h = roi
        # dst = dst[y:y+h, x:x+w]
        # cv2.imwrite('caliResult2.png', dst)

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
            # cv2.putText(self.contoured_image, str(merr[i]), (merr[i]), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 2)

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
            # elif areas[i] < (np.mean(areas) - (np.mean(areas)*(0.2))):
            #     aerr.append(i)
            # elif areas[i] == 0:
            #     aerr.append(i)
        # filtered_areas = [value for index, value in enumerate(areas) if index not in aerr]
        # print('filtered area errors',filtered_areas)
        # filtered_midpoint = [value for index, value in enumerate(midpoint) if index not in aerr]
        # print(len(filtered_midpoint))
        # for point in merr:
        #     print(point)
        # merr = self.sort_point(merr)

        return merr, aerr

    def sort_point(self, points):
        sum_value = [sum(point) for point in points]
        sorted_value = [val for _, val in sorted(zip(sum_value, points), reverse=True)]
        # for i in range(len(sorted_value)):
        #     print(points[i], sum_value[i], sorted_value[i], i+1)
        return sorted_value
            

    def ShowImage(self, window_name, image):
        plt.title(window_name)
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.show()

    def Get_Binary(self):
        return self.morph
    
    def Save_Image(self, file_name, image):
        cv2.imwrite(file_name, image)

    def export_points(self, points, name):
        data = pd.DataFrame(points)
        data.to_csv(name, index=False)

if __name__ == '__main__':
    # Find = TrayFinder(file_path='C:/Project/FinalProject/Images/test_image_cam_jig2_0.png')
    # mid_points = Find.FindMidpoint()
    # mid_points.sort(axis=1)
    # print(mid_points)
    # Find.FindMidpoint()
    # Find.ShowImage('midpoints', Find.contoured_image)
    # Find.ShowImage('blur', Find.morph)
    paths = glob.glob("C:/Project/FinalProject/MainPackage/ImageProcessing/images/*.png")
    count = 0
    # Test1 = TrayFinder(paths[4])
    # mid = Test1.FindMidpoint()
    for file_path in paths:
        count += 1
        tray_finder = TrayFinder(file_path)
        tray_finder.FindMidpoint()
        tray_finder.ShowImage(f'midpoint{count}', tray_finder.contoured_image)
        # tray_finder.ShowImage(f'gray{count}', tray_finder.morph)
        tray_finder.Save_Image(f'result{count}.png', tray_finder.contoured_image)
        tray_finder.export_points(name = f'result{count}.csv', points= tray_finder.merr)
    # test1 = TrayFinder(paths[0])
    # test1.FindMidpoint()
    # test1.ShowImage('test1', test1.contoured_image)
    # test1.Save_Image('resultX.png', test1.contoured_image)
    
