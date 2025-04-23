import cv2
import numpy as np

# Global variables for region selection
roi_selected = False
ref_point = []
cropping = False
roi = None

def select_region(event, x, y, flags, param):
    """Mouse callback to select ROI."""
    global ref_point, cropping, roi_selected

    if event == cv2.EVENT_LBUTTONDOWN:
        ref_point = [(x, y)]
        cropping = True

    elif event == cv2.EVENT_MOUSEMOVE and cropping:
        temp_img = param.copy()
        cv2.rectangle(temp_img, ref_point[0], (x, y), (0, 255, 0), 2)
        cv2.imshow("Video", temp_img)

    elif event == cv2.EVENT_LBUTTONUP:
        ref_point.append((x, y))
        cropping = False
        roi_selected = True
        cv2.rectangle(param, ref_point[0], ref_point[1], (0, 255, 0), 2)
        cv2.imshow("Video", param)

def click_to_detect(event, x, y, flags, param):
    """Mouse callback to handle outlining and masking with left and right clicks."""
    global roi

    if event == cv2.EVENT_LBUTTONDOWN and roi_selected:
        # Outline the object
        roi_hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        clicked_color = roi_hsv[y, x]
        lower_bound = np.array([max(0, clicked_color[0] - 10), 50, 50])
        upper_bound = np.array([min(179, clicked_color[0] + 10), 255, 255])
        mask = cv2.inRange(roi_hsv, lower_bound, upper_bound)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            cv2.drawContours(roi, [contour], -1, (0, 255, 0), 2)  # Green outline

        cv2.imshow("ROI with Outline", roi)
        print("Object outlined. Right-click to create the mask.")

    elif event == cv2.EVENT_RBUTTONDOWN and roi_selected:
        # Create the mask
        roi_hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        clicked_color = roi_hsv[y, x]
        lower_bound = np.array([max(0, clicked_color[0] - 10), 50, 50])
        upper_bound = np.array([min(179, clicked_color[0] + 10), 255, 255])
        mask = cv2.inRange(roi_hsv, lower_bound, upper_bound)

        cv2.imshow("Mask", mask)
        print("Mask created. You can restart by selecting a new region or re-running.")

cap = cv2.VideoCapture(0)  # Use 0 for webcam or video file path

while True:
    ret, frame = cap.read()
    if not ret:
        break

    if not roi_selected:
        cv2.imshow("Video", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("r"):  # Press 'r' to select ROI
        roi_selected = False
        ref_point = []
        clone = frame.copy()
        cv2.setMouseCallback("Video", select_region, clone)
        cv2.waitKey(0)

    if roi_selected:
        x1, y1 = ref_point[0]
        x2, y2 = ref_point[1]
        roi = frame[y1:y2, x1:x2]
        cv2.imshow("ROI", roi)
        cv2.setMouseCallback("ROI", click_to_detect)

    if key == ord("q"):  # Quit
        break

cap.release()
cv2.destroyAllWindows()
