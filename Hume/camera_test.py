import cv2
import time
import asyncio
import traceback
import os
import requests

from hume import HumeStreamClient
from hume.models.config import FaceConfig

def get_top_3_emotions(emotions):
    sorted_emotions = sorted(emotions, key=lambda x: x['score'], reverse=True)
    top_3_emotions = sorted_emotions[:3]
    return top_3_emotions

def get_emotions(result):
    if "predictions" not in result["face"]:
        print("No face detected")
        return
    else:
        emotions = result["face"]["predictions"][0]["emotions"]
        return get_top_3_emotions(emotions)

def detected_Confusion(emotions):
    for emotion in emotions:
        if emotion['name'] == 'Confusion':
            return True

async def send_to_api(filepath):
    try:
        client = HumeStreamClient("YOKvO8EbtQ5bRXuBWVJGtbie49cUP5MXXHA1gf0z7xvEtahB")

        # Enable face identification to track unique faces over the streaming session
        config = FaceConfig(identify_faces=True)
        async with client.connect([config]) as socket:
            result = await socket.send_file(filepath)
            emotions = get_emotions(result)
            top_3_emotions = get_top_3_emotions(emotions)
            print(top_3_emotions)
            if detected_Confusion(top_3_emotions):
                url = 'http://127.0.0.1:5000/api/confusion-detected'
                response = requests.post(url)

                if response.status_code == 200:
                    print('POST request successful')
                    print('request get:')
                    print(requests.get(url).text)
                    global stop_processing
                    stop_processing = True

                else:
                    print('POST request failed')
    except Exception:
        print(traceback.format_exc())

def capture_frames():
    global stop_processing
    stop_processing = False

    # Initialize the camera
    capture = cv2.VideoCapture(0)  # 0 represents the default camera, change if necessary
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Get the current time
    start_time = time.time()

    while True:
        # Read a frame from the camera
        ret, frame = capture.read()

        # Display the frame in a window
        cv2.imshow('Camera', frame)

        # Check if 1 second has passed
        if time.time() - start_time >= 1.0 and not stop_processing:
            # Reset the timer
            start_time = time.time()

            # Perform your desired processing on the frame here
            # For example, you can perform any additional operations on the 'frame' variable

            # Save the frame as an image file
            filepath = os.path.join(current_dir, "captured_frame.jpg")
            cv2.imwrite(filepath, frame)

            # Pass the captured frame to the API asynchronously
            asyncio.run(send_to_api(filepath))

        # Wait for 1 millisecond and check for user input
        if cv2.waitKey(1) == ord('q'):  # Press 'q' to exit the loop
            break

    # Release the camera and close the windows
    capture.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    capture_frames()