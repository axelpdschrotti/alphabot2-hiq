from picamera2 import Picamera2
import cv2

picam2 = Picamera2()
picam2.start()
picam2.capture_file("test.jpg")

frame = picam2.capture_array()
cv2.imshow("Camera", frame)
cv2.waitKey(0)
cv2.destroyAllWindows()