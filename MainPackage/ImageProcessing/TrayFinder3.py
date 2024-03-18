import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import glob
import pickle

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
    def Undistorted(self, image):
        with open('MainPackage/ImageProcessing/CalibrationMatrices/cameraMatrix.pkl', 'rb') as f1:
            cameraMatrix = pickle.load(f1)
        
        with open('MainPackage/ImageProcessing/CalibrationMatrices/dist.pkl', 'rb') as f2:
            dist = pickle.load(f2)
        
        h, w = image.shape[:2]
        newCameraMatrix, roi = cv2.getOptimalNewCameraMatrix(cameraMatrix, dist, (w,h), 1, (w,h))

        #undistort
        # dst = cv2.undistort(image, cameraMatrix, dist, None, newCameraMatrix)
        #crop the image
        # x, y, w, h = roi
        # dst = dst[y:y+h, x:x+w]
        # cv2.imwrite('caliResult1.png', dst)

        mapx, mapy = cv2.initUndistortRectifyMap(cameraMatrix, dist, None, newCameraMatrix, (w,h), 5)
        dst = cv2.remap(image, mapx, mapy, cv2.INTER_LINEAR)

        # crop the image
        x, y, w, h = roi
        dst = dst[y:y+h, x:x+w]
        # cv2.imwrite('caliResult2.png', dst)
        self.image = dst

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
        # print(self.merr)
        # points=[]
        # for 
        points = self.Find_Closest(self.merr)

        for i in range(len(points) -1 ):
            cv2.line(self.contoured_image, tuple(points[i]), tuple(points[i+1]), (0,0,0), thickness=2)

        for i in range(len(self.merr)):
            cv2.putText(self.contoured_image, str(i+1), (points[i] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.circle(self.contoured_image, (points[i]), radius=2, color=(255, 255, 255), thickness=-1)
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

    def Find_Closest(self, points):

        def Starter(points):
            start_index = np.argmin(np.sum(points, axis=1))
            points[0], points[start_index] = points[start_index], points[0]
            return points
        points = Starter(points)
        points = np.array(points)

        def IsIn(a_point, points):
            a_point_tuple = tuple(a_point)
            points_tuples = [tuple(p) for p in points]
            in_list = a_point_tuple in points_tuples

            return in_list

        def Distance_Cal(index, points):
            if index < 0 or index >= len(points):
                raise ValueError("Index is out of bounds")
            ref_point = points[index]
            distances = np.linalg.norm(points - ref_point, axis=1)

            return distances
        
        new_points = [points[0]]
        index = 0
        indexer = [0]
        while len(new_points) != len(points):
        
            distances = Distance_Cal(index, points)
            distances[index] = np.inf
            closest_index = np.argmin(distances)
            closest_point = points[closest_index]
            if IsIn(closest_point, new_points) == False:
                print(f"index {index} is not in new_points")
                new_points.append(closest_point)
                index = closest_index
                indexer.append(index)
                print(indexer)
            elif IsIn(closest_point, new_points) == True:
                print(f"index {index} is in new_points")

                for i in indexer:
                    distances[i] = np.inf
                closest_index = np.argmin(distances)
                print(closest_index, closest_point)
                closest_point = points[closest_index]
                new_points.append(closest_point)
                print(distances)
                index = closest_index
                indexer.append(index)
        return new_points
            
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
    paths = glob.glob("MainPackage\ImageProcessing\images\*.png")
    count = 0
    # testing = TrayFinder(paths[0])
    # # testing.ShowImage('raw image', image=testing.image)
    # testing.FindMidpoint()
    # # testing.ShowImage('midpoints', image=testing.contoured_image)
    # testing.Save_Image('result.png', image=testing.contoured_image)
    # print(type(testing.merr))
    # points= []
    # for i in range(len(testing.merr)):
    #     # print(type(testing.merr[i].tolist()))
    #     points.append(testing.merr[i].tolist())
    # # print(points.shape)
    # new_points = testing.Find_Closest(points)
    # testing.export_point(points= testing.merr, name='points.csv')
    for file_path in paths:
        count += 1
        testing = TrayFinder(file_path)
        testing.Undistorted(testing.image)
        testing.FindMidpoint()
        # testing.ShowImage(f'TestingResults/midpoint{count}', testing.contoured_image)
        # testing.ShowImage(f'gray{count}', testing.morph)
        testing.Save_Image(f'TestingResults/result{count}.png', testing.contoured_image)
        testing.export_points(name = f'TestingResults/Mapping{count}.csv', points= testing.merr)
