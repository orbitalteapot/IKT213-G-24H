import cv2

cap = cv2.VideoCapture("tcp://192.168.1.10:5556", cv2.CAP_FFMPEG)
while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow('TCP Stream', frame)
    if cv2.waitKey(1) == 27:  # ESC to quit
        break
cap.release()
cv2.destroyAllWindows()
