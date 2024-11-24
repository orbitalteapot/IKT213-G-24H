import cv2
import time

# Initialize two Picamera2 instances for each camera port
frame_left = cv2.VideoCapture(2)
frame_right = cv2.VideoCapture(0)

# Set resolution and frame rate for both cameras
# frame_left.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
# frame_left.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
# frame_left.set(cv2.CAP_PROP_FPS, 5)
frame_left.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # Disable auto-focus
frame_left.set(cv2.CAP_PROP_FOCUS, 1)  # Set a fixed focus value

# frame_right.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
# frame_right.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
# frame_right.set(cv2.CAP_PROP_FPS, 5)
frame_right.set(cv2.CAP_PROP_AUTOFOCUS, 0)
frame_right.set(cv2.CAP_PROP_FOCUS, 1)

# Allow cameras to warm up
time.sleep(2)
num = 0

try:
    while True:
        # Capture frames from each camera
        ret_left, frame_left_img = frame_left.read()
        ret_right, frame_right_img = frame_right.read()

        # Check if frames are successfully captured
        if not ret_left or not ret_right:
            print("Failed to capture images from one or both cameras.")
            break

        k = cv2.waitKey(5)

        if k == 27:
            break
        elif k == ord('s'):  # wait for 's' key to save and exit
            # cv2.imwrite('2D_imageL.png', frame_left)
            cv2.imwrite('RectificationImages/stereoLeft/imageL' + str(num) + '.png', frame_left_img)
            cv2.imwrite('RectificationImages/stereoRight/imageR' + str(num) + '.png', frame_right_img)
            print("images saved!")
            num += 1

        # Display the frames in separate OpenCV windows
        cv2.imshow("Left Camera Feed", frame_left_img)
        cv2.imshow("Right Camera Feed", frame_right_img)

        # Break on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    # Release resources for both cameras
    frame_left.release()
    frame_right.release()
    cv2.destroyAllWindows()
