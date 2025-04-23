import numpy as np
import cv2 as cv
import glob
 
# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
chessBoardDimensions = (9,7) #length x height
 
# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((np.prod(chessBoardDimensions),3), np.float32)
objp[:,:2] = np.mgrid[0:chessBoardDimensions[0],0:chessBoardDimensions[1]].T.reshape(-1,2)
 
# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.
"""
images = glob.glob('*.jpg')
 
for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
 
    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, chessBoardDimensions, None)
 
    # If found, add object points, image points (after refining them)
    if ret:
        print(f"Success: {fname}")  # Log successful detections
        objpoints.append(objp)
 
        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)
 
        # Draw and display the corners
        cv.drawChessboardCorners(img, chessBoardDimensions, corners2, ret)
        cv.imshow('img', img)
        cv.waitKey(500)
    else:
        print(f"Failed: {fname}")  # Log failed detections
 
cv.destroyAllWindows()

ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
"""
#######For Video Undistortion########
with np.load('calibration_data.npz') as data:
    mtx = data['mtx']
    dist = data['dist']
    mtx1 = data['mtx']
    dist1 = data['dist']

cap = cv.VideoCapture(0)
cap1 = cv.VideoCapture(1)

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

        # Capture frame-by-frame
    ret1, frame1 = cap1.read()
    
    # Get the frame dimensions
    h1, w1 = frame1.shape[:2]

    
    # Get the optimal new camera matrix
    newcameramtx1, roi1 = cv.getOptimalNewCameraMatrix(mtx1, dist1, (w1, h1), 1, (w1, h1))
    
    # Undistort the frame
    undistorted_frame1 = cv.undistort(frame1, mtx1, dist1, None, newcameramtx1)
    
    # Crop the frame
    x1, y1, w1, h1 = roi1
    undistorted_frame1 = undistorted_frame1[y1:y1+h1, x1:x1+w1]
    
    # Display the resulting frame
    cv.imshow('Undistorted Live Feed1', undistorted_frame1)
    
    # Break the loop if 'q' is pressed
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv.destroyAllWindows()

