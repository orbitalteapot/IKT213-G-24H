import cv2
import threading


class CameraStream:
    def __init__(self, rtsp_url):
        self.rtsp_url = rtsp_url
        self.cap = cv2.VideoCapture(rtsp_url)
        self.frame = None
        self.stopped = False

    def start(self):
        threading.Thread(target=self.update, daemon=True).start()
        return self

    def update(self):
        while not self.stopped:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    self.frame = frame
                else:
                    print(f"Error: Unable to read frame from {self.rtsp_url}")
            else:
                print(f"Error: Unable to open stream {self.rtsp_url}")
                self.stopped = True

    def get_frame(self):
        return self.frame

    def stop(self):
        self.stopped = True
        self.cap.release()


# Define RTSP URLs for both cameras
camera_1_url = "rtsp://<camera1_ip>:<5000>/<path>"
camera_2_url = "rtsp://<camera2_ip>:<port>/<path>"

# Create and start camera streams
camera1 = CameraStream(camera_1_url).start()
camera2 = CameraStream(camera_2_url).start()

try:
    while True:
        # Retrieve the latest frames
        frame1 = camera1.get_frame()
        frame2 = camera2.get_frame()

        # Display Camera 1
        if frame1 is not None:
            cv2.imshow("Camera 1", frame1)

        # Display Camera 2
        if frame2 is not None:
            cv2.imshow("Camera 2", frame2)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    # Stop the streams and close OpenCV windows
    camera1.stop()
    camera2.stop()
    cv2.destroyAllWindows()
