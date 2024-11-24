# camera_interface.py
import cv2 as cv


class CameraInterface:
    def __init__(self, resolution):
        self.resolution = resolution  # Camera initialization logic here

    def getcamera(self):
        # Open cameras
        frame_left = cv.VideoCapture(2)
        frame_right = cv.VideoCapture(0)

        # Set resolution (should match the calibration resolution)

        # frame_left.set(cv.CAP_PROP_FRAME_WIDTH, 640)
        # frame_left.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
        frame_left.set(cv.CAP_PROP_AUTOFOCUS, 0)
        frame_left.set(cv.CAP_PROP_FOCUS, 1)

        # frame_right.set(cv.CAP_PROP_FRAME_WIDTH, 640)
        # frame_right.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
        frame_right.set(cv.CAP_PROP_AUTOFOCUS, 0)
        frame_right.set(cv.CAP_PROP_FOCUS, 1)
        return frame_left, frame_right
