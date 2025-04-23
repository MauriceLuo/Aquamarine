
import cv2

cam = cv2.VideoCapture(0)

cv2.namedWindow("test")

img_counter = 0

while True:
    ret, frame = cam.read()
    if not ret:
        print("failed to grab frame")
        break
    cv2.imshow("test", frame)

    k = cv2.waitKey(1)
    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k%256 == 32:
        # SPACE pressed
        img_name = "right11.jpg".format(img_counter)
        cv2.imwrite(img_name, frame)
        print("{} written!".format(img_name))
        img_counter += 1

cam.release()

cv2.destroyAllWindows()

"""
import cv2

camL = cv2.VideoCapture(0)
camR = cv2.VideoCapture(1)

cv2.namedWindow("Left")
cv2.namedWindow("Right")

img_counter = 0

while True:
    retL, frameL = camL.read()
    retR, frameR = camR.read()

    cv2.imshow("camL", frameL)
    cv2.imshow("camR", frameR)

    k = cv2.waitKey(1)
    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break    
    
    elif k%256 == 108:
        # L pressed
        cv2.imwrite("left", frameL)
        print("left written!")

    elif k%256 == 114:
        # SPACE pressed
        cv2.imwrite("right", frameR)
        print("left written!")

    



camL.release()
camR.release()

cv2.destroyAllWindows()

"""

