import cv2
import tensorflow as tf

# Load the pre-trained model
model = tf.saved_model.load("ssd_mobilenet_v2_coco/saved_model")

# Capture an image using OpenCV (or Picamera2 if you're using a Pi Camera)
cap = cv2.VideoCapture(0)
ret, frame = cap.read()

# Convert to RGB
rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

# Run object detection
input_tensor = tf.convert_to_tensor(rgb_frame)
input_tensor = input_tensor[tf.newaxis,...]
output_dict = model(input_tensor)

# Process the output (bounding boxes, labels, scores)
# (code for drawing bounding boxes omitted for brevity)

cv2.imshow("Object Detection", frame)
cv2.waitKey(0)
cv2.destroyAllWindows()
cap.release()
