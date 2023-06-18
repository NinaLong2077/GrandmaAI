import cv2
import time

def capture_frames():
    # Initialize the camera
    capture = cv2.VideoCapture(0)  # 0 represents the default camera, change if necessary

    # Get the current time
    start_time = time.time()

    while True:
        # Read a frame from the camera
        ret, frame = capture.read()

        # Display the frame in a window
        cv2.imshow('Camera', frame)

        # Check if 1 second has passed
        if time.time() - start_time >= 1.0:
            # Reset the timer
            start_time = time.time()

            # Perform your desired processing on the frame here
            # For example, you can perform any additional operations on the 'frame' variable

            # Display the captured frame in a separate window
            cv2.imshow('Captured Image', frame)

        # Wait for 1 millisecond and check for user input
        if cv2.waitKey(1) == ord('q'):  # Press 'q' to exit the loop
            break

    # Release the camera and close the windows
    capture.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    capture_frames()
