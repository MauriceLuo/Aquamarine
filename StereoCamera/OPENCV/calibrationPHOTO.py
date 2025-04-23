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

#np.savez('calibration_data1.npz', mtx=mtx, dist=dist)

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

print(f'ret: {ret}')
print(f'mtx: {mtx}')
print(f'dist: {dist}')
print(f'rvecs: {rvecs}')
print(f'tvecs: {tvecs}')

mean_error = 0
for i in range(len(objpoints)):
    imgpoints2, _ = cv.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
    error = cv.norm(imgpoints[i], imgpoints2, cv.NORM_L2)/len(imgpoints2)
    mean_error += error
 
print( "total error: {}".format(mean_error/len(objpoints)) )

