import cv2 as cv
import numpy as np
import glob

# Define the dimensions of the checkerboard
CHECKERBOARD = (9, 7)  # 8x6 checkerboard pattern

# Termination criteria for the cornerSubPix algorithm
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Prepare object points: (0,0,0), (1,0,0), (2,0,0) ... (7,5,0)
objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)

# Arrays to store object points and image points from all images
objpoints = []  # 3D points in real world space
imgpoints = []  # 2D points in image plane

# Load all images of the checkerboard pattern (replace with your own images)
images = glob.glob('*.jpg')


image_shape = None

for fname in images:
    img = cv.imread(fname)
    
    # Convert the image to grayscale
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    
    # Set image shape (height, width) for calibration later
    if image_shape is None:
        image_shape = gray.shape[::-1]  # (width, height)

    # Find the checkerboard corners
    ret, corners = cv.findChessboardCorners(gray, CHECKERBOARD, None)

    if ret:
        objpoints.append(objp)  # Add object points
        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)  # Refine and add image points

        # Draw and display the corners
        cv.drawChessboardCorners(img, CHECKERBOARD, corners2, ret)
        cv.imshow('Checkerboard', img)
        cv.waitKey(500)

cv.destroyAllWindows()

# Now perform camera calibration using the object points and image points
ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, image_shape, None, None)

# Print the camera matrix and distortion coefficients
print("Camera matrix:\n", camera_matrix)
print("Distortion coefficients:\n", dist_coeffs)

# Save the camera matrix and distortion coefficients for later use
np.savez('calibration_data.npz', mtx=camera_matrix, dist=dist_coeffs)