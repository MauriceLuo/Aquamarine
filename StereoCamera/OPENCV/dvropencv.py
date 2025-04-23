import cv2 as cv
import numpy as np

with np.load('calibration_data.npz') as data:
    mtx1 = data['mtx']
    dist1 = data['dist']
# Assume these are the calibration matrices obtained from the previous code for each camera
# Replace these placeholders with the actual calibration values for each camera
#mtx1, dist1 = ...  # Camera 1 (Top-left) calibration data
#mtx2, dist2 = ...  # Camera 2 (Top-right) calibration data
#mtx3, dist3 = ...  # Camera 3 (Bottom-left) calibration data
#mtx4, dist4 = ...  # Camera 4 (Bottom-right) calibration data

# Capture the single video feed that contains the 4 camera views in a 2x2 grid
cap = cv.VideoCapture(0)  # Or use the appropriate source

# Loop to capture and display the live feed
while True:
    # Capture a frame from the video capture
    ret, frame = cap.read()
    if not ret:
        print("Error capturing video feed.")
        break

    # Get frame dimensions (assuming the DVR feed is a 2x2 grid)
    h, w = frame.shape[:2]

    # Assuming the feed is split into 4 equal quadrants, calculate the dimensions of each quadrant
    h_quad, w_quad = h // 2, w // 2

    # Split the frame into the 4 quadrants
    top_left = frame[0:h_quad, 0:w_quad]       # Top-left (Camera 1)
    top_right = frame[0:h_quad, w_quad:w]      # Top-right (Camera 2)
    bottom_left = frame[h_quad:h, 0:w_quad]    # Bottom-left (Camera 3)
    bottom_right = frame[h_quad:h, w_quad:w]   # Bottom-right (Camera 4)

    # Undistort each quadrant using the corresponding calibration data

    # Camera 1 (Top-left)
    newcameramtx1, roi1 = cv.getOptimalNewCameraMatrix(mtx1, dist1, (w_quad, h_quad), 1, (w_quad, h_quad))
    undistorted_top_left = cv.undistort(top_left, mtx1, dist1, None, newcameramtx1)
    x1, y1, w1, h1 = roi1
    undistorted_top_left = undistorted_top_left[y1:y1+h1, x1:x1+w1]
    undistorted_top_left = cv.resize(undistorted_top_left, (w_quad, h_quad))  # Resize back if cropped
    """
    # Camera 2 (Top-right)
    newcameramtx2, roi2 = cv.getOptimalNewCameraMatrix(mtx2, dist2, (w_quad, h_quad), 1, (w_quad, h_quad))
    undistorted_top_right = cv.undistort(top_right, mtx2, dist2, None, newcameramtx2)
    x2, y2, w2, h2 = roi2
    undistorted_top_right = undistorted_top_right[y2:y2+h2, x2:x2+w2]
    undistorted_top_right = cv.resize(undistorted_top_right, (w_quad, h_quad))

    # Camera 3 (Bottom-left)
    newcameramtx3, roi3 = cv.getOptimalNewCameraMatrix(mtx3, dist3, (w_quad, h_quad), 1, (w_quad, h_quad))
    undistorted_bottom_left = cv.undistort(bottom_left, mtx3, dist3, None, newcameramtx3)     
    x3, y3, w3, h3 = roi3
    undistorted_bottom_left = undistorted_bottom_left[y3:y3+h3, x3:x3+w3]
    undistorted_bottom_left = cv.resize(undistorted_bottom_left, (w_quad, h_quad))

    # Camera 4 (Bottom-right)
    newcameramtx4, roi4 = cv.getOptimalNewCameraMatrix(mtx4, dist4, (w_quad, h_quad), 1, (w_quad, h_quad))
    undistorted_bottom_right = cv.undistort(bottom_right, mtx4, dist4, None, newcameramtx4)
    x4, y4, w4, h4 = roi4
    undistorted_bottom_right = undistorted_bottom_right[y4:y4+h4, x4:x4+w4]
    undistorted_bottom_right = cv.resize(undistorted_bottom_right, (w_quad, h_quad))
    """

    # Combine the undistorted quadrants back into a single composite frame
    top_row = np.hstack((undistorted_top_left, top_right))
    bottom_row = np.hstack((bottom_left, bottom_right))
    composite_frame = np.vstack((top_row, bottom_row))

        # Display the composite frame
    cv.imshow('DVR Feed with Undistorted Cameras', composite_frame)

    # Check if the user pressed the 'q' key to exit
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

# Release video capture and close windows
cap.release()
cv.destroyAllWindows()