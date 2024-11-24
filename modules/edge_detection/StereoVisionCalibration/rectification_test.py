import cv2 as cv
import numpy as np

from modules.edge_detection.calibration import Rectification

# Open cameras
frame_left = cv.VideoCapture(2)
frame_right = cv.VideoCapture(0)

# Set resolution (should match the calibration resolution)
frame_left.set(cv.CAP_PROP_FRAME_WIDTH, 640)
frame_left.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
frame_right.set(cv.CAP_PROP_FRAME_WIDTH, 640)
frame_right.set(cv.CAP_PROP_FRAME_HEIGHT, 480)

# Display the rectified frames
while True:
    ret_left, frame_left_img = frame_left.read()
    ret_right, frame_right_img = frame_right.read()

    if not ret_left or not ret_right:
        print("Failed to capture images from one or both cameras.")
        break

    rectified_left, rectified_right = Rectification.undistortrectify(frame_left_img, frame_right_img)

    # Concatenate frames horizontally for side-by-side view
    combined = np.hstack((rectified_left, rectified_right))
    cv.imshow("Rectified Stereo View", combined)

    # Break on 'q' key press
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
frame_left.release()
frame_right.release()
cv.destroyAllWindows()
