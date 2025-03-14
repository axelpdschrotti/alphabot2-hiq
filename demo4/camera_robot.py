import cv2

def main():
    # Open the default camera (device 0)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Cannot open camera")
        return

    while True:
        ret, frame = cap.read()  # Capture frame-by-frame
        if not ret:
            print("Error: Cannot receive frame")
            break

        cv2.imshow('Alphabot2 Pi Camera', frame)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('s'):  # Press 's' to save a snapshot
            cv2.imwrite('snapshot.jpg', frame)
            print("Snapshot saved as snapshot.jpg")

    # Release the capture and close any OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
