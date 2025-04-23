import cv2
import numpy as np

# Global variables for HSV range, toggle, and vertical reference line
lower_bound = np.array([0, 0, 0])
upper_bound = np.array([179, 255, 255])
check_negative = False  # Toggle for checking the negative area
vertical_line_x = 816  # Default x-coordinate for the vertical reference line

# Callback functions for HSV range adjustment
def update_lower_h(val):
    lower_bound[0] = val

def update_upper_h(val):
    upper_bound[0] = val

def update_lower_s(val):
    lower_bound[1] = val

def update_upper_s(val):
    upper_bound[1] = val

def update_lower_v(val):
    lower_bound[2] = val

def update_upper_v(val):
    upper_bound[2] = val

def main():
    global check_negative, vertical_line_x

    # Load the image
    image = cv2.imread('right0 copy.png')  # Replace 'image.jpg' with your image file
    if image is None:
        print("Error: Could not load the image.")
        return

    # Select the ROI interactively
    roi = cv2.selectROI("Select ROI", image, showCrosshair=True, fromCenter=False)
    cv2.destroyWindow("Select ROI")  # Close the ROI selection window

    # Check if ROI was selected
    if roi == (0, 0, 0, 0):
        print("No ROI selected.")
        return

    # Extract the selected region
    x, y, w, h = map(int, roi)
    selected_region = image[y:y+h, x:x+w]

    # Convert the ROI to HSV color space
    hsv_roi = cv2.cvtColor(selected_region, cv2.COLOR_BGR2HSV)

    # Create a window for HSV adjustment
    cv2.namedWindow("HSV Adjustment")

    # Create trackbars for HSV adjustment
    cv2.createTrackbar("Lower H", "HSV Adjustment", 0, 179, update_lower_h)
    cv2.createTrackbar("Upper H", "HSV Adjustment", 179, 179, update_upper_h)
    cv2.createTrackbar("Lower S", "HSV Adjustment", 0, 255, update_lower_s)
    cv2.createTrackbar("Upper S", "HSV Adjustment", 255, 255, update_upper_s)
    cv2.createTrackbar("Lower V", "HSV Adjustment", 0, 255, update_lower_v)
    cv2.createTrackbar("Upper V", "HSV Adjustment", 255, 255, update_upper_v)

    while True:
        # Reset the display region to the original image
        display_region = image.copy()

        # Create a mask for the ROI based on the updated HSV range
        mask = cv2.inRange(hsv_roi, lower_bound, upper_bound)

        # Choose positive or negative area based on the toggle
        if check_negative:
            mask = cv2.bitwise_not(mask)  # Invert mask for negative area

        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Combine all contours into one bounding rectangle
            all_points = np.vstack(contours)
            x_combined, y_combined, w_combined, h_combined = cv2.boundingRect(all_points)

            # Map the rectangle coordinates back to the full image
            x_combined += x
            y_combined += y

            # Draw the bounding rectangle
            cv2.rectangle(display_region, (x_combined, y_combined),
                          (x_combined + w_combined, y_combined + h_combined), (0, 255, 0), 2)

            # Calculate the distances from the reference line to the rectangle edges
            left_distance = abs(vertical_line_x - x_combined)
            right_distance = abs(vertical_line_x - (x_combined + w_combined))

            # Display width, height, and distances
            width_text = f"Width: {w_combined}px"
            height_text = f"Height: {h_combined}px"
            left_text = f"Left Dist: {left_distance}px"
            right_text = f"Right Dist: {right_distance}px"

            cv2.putText(display_region, width_text,
                        (x_combined + 5, y_combined + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.putText(display_region, height_text,
                        (x_combined + 5, y_combined + h_combined - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.putText(display_region, left_text,
                        (vertical_line_x + 5, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            cv2.putText(display_region, right_text,
                        (vertical_line_x + 5, y + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

        # Draw the vertical reference line on the full image
        cv2.line(display_region, (vertical_line_x, 0), (vertical_line_x, image.shape[0]), (255, 0, 0), 1)

        # Display whether calculating positive or negative area
        area_type = "Negative Area" if check_negative else "Positive Area"
        cv2.putText(display_region, area_type, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Show the result
        cv2.imshow("Detected Object", display_region)
        cv2.imshow("Mask", mask)

        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # Quit the program
            break
        elif key == ord('t'):  # Toggle positive/negative area
            check_negative = not check_negative
        elif key == ord('a'):  # Move vertical line left
            vertical_line_x = max(0, vertical_line_x - 5)
        elif key == ord('d'):  # Move vertical line right
            vertical_line_x = min(image.shape[1], vertical_line_x + 5)

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
