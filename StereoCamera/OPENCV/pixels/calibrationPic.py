import numpy as np
import cv2 as cv
import glob
 
with np.load('calibration_data.npz') as data:
    mtx = data['mtx']
    dist = data['dist']

with np.load('calibration_data1.npz') as data:
    mtx1 = data['mtx']
    dist1 = data['dist']

########For getting calibresult########

img = cv.imread(f'right copy.jpg')
h,  w = img.shape[:2]
newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

# undistort
dst = cv.undistort(img, mtx, dist, None, newcameramtx)
 
# crop the image
x, y, w, h = roi
dst = dst[y:y+h, x:x+w]
cv.imwrite(f'right0.png', dst)



########For getting calibresult2########

img1 = cv.imread(f'left copy.jpg')
h1,  w1 = img1.shape[:2]
newcameramtx1, roi1 = cv.getOptimalNewCameraMatrix(mtx1, dist1, (w1,h1), 1, (w1,h1))

# undistort
dst1 = cv.undistort(img1, mtx1, dist1, None, newcameramtx1)
 
# crop the image
x1, y1, w1, h1 = roi1
dst1 = dst1[y1:y1+h1, x1:x1+w1]
cv.imwrite(f'left0.png', dst1)






