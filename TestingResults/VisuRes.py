import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import glob

mapping_frames = []
undist_frames =[]
points_frames = []

for mapping in glob.glob('TestingResults/Mapping?.csv'):
    df = pd.read_csv(mapping)
    mapping_frames.append(df)
for undist in glob.glob('TestingResults/Undist?.csv'):
    df = pd.read_csv(undist)
    undist_frames.append(df)
for points in glob.glob('TestingResults/RawPoints?.csv'):
    df = pd.read_csv(points)
    points_frames.append(df)

# for i in range(len(points_frames)):
#     print(points_frames[i]['0'])
#plotting
plt.figure()
for i in range(len(points_frames)-1):
    plt.subplot(2,3,i+1)
    plt.title(f'image {i}')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.scatter(points_frames[i]['0'], points_frames[i]['1'], color='blue', marker='*', alpha=0.75, edgecolors='k')
    plt.scatter(undist_frames[i]['0'], undist_frames[i]['1'], color='green', marker='o', alpha=0.75, edgecolors='k')
    plt.scatter(mapping_frames[i]['0'], mapping_frames[i]['1'], color='red', marker='^', alpha=0.75, edgecolors='k')
    # plt.legend(loc='upper right')

plt.show()