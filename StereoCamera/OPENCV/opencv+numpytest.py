import numpy as np
import cv2 as cv
import glob

with np.load('calibration_data1.npz') as data:
    mtx = data['mtx']
    dist = data['dist']
"""
########For getting calibresult########

imageIndex = np.random.randint(20)
print(f'calibrating opencv_frame_{imageIndex}.jpg')
img = cv.imread(f'opencv_frame_{imageIndex}.jpg')
h,  w = img.shape[:2]
newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

# undistort
dst = cv.undistort(img, mtx, dist, None, newcameramtx)
 
# crop the image
x, y, w, h = roi
dst = dst[y:y+h, x:x+w]
cv.imwrite(f'calibresult{imageIndex}.png', dst)
print(f'calibrated opencv_frame_{imageIndex}.jpg')
"""

cap = cv.VideoCapture(0)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    
    # Get the frame dimensions
    h, w = frame.shape[:2]

    
    # Get the optimal new camera matrix
    newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
    
    # Undistort the frame
    undistorted_frame = cv.undistort(frame, mtx, dist, None, newcameramtx)
    
    # Crop the frame
    x, y, w, h = roi
    undistorted_frame = undistorted_frame[y:y+h, x:x+w]
    
    # Display the resulting frame
    cv.imshow('Undistorted Live Feed', undistorted_frame)
    
    # Break the loop if 'q' is pressed
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv.destroyAllWindows()