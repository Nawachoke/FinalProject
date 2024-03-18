import numpy as np
import matplotlib.pyplot as plt
import cv2
import pandas as pd
import math

points = [[ 57, 401],
        [137, 400],
        [215, 398],
        [374, 395],
        [296, 395],
        [449, 393],
        [132, 243],
        [ 52, 243],
        [211, 243],
        [369, 240],
        [293, 241],
        [446, 239],
        [206,  85],
        [ 48,  85],
        [127,  84],
        [443,  82],
        [367,  83],
        [287,  83]]

def Find_Closest(points):
    def Starter(points):
        start_index = np.argmin(np.sum(points, axis=1))
        points[0], points[start_index] = points[start_index], points[0]
        return points
    points = Starter(points)
    points = np.array(points)
    # print(points.shape)

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

new_points = Find_Closest(points)

image = np.zeros((500, 500, 3), dtype=np.uint8)

for i in range(len(new_points)-1):
    cv2.line(image, tuple(new_points[i]), tuple(new_points[i+1]), (255, 255, 255), thickness=2)

for i, point in enumerate(new_points):
    cv2.circle(image, tuple(point), 5, (0, 255, 0), -1)  # Green color, filled circle
    cv2.putText(image, f"({point[0]},{point[1]})({i})", (point[0] - 20, point[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255))
# Display the image
cv2.imshow("Reversed S-Curve Line with Given Points", image)
cv2.imwrite('res.png', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
