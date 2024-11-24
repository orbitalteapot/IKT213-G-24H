import cv2


class Rectification:
    def __init__(self):
        # Camera parameters to undistort and rectify images
        cv_file = cv2.FileStorage()
        cv_file.open('stereoMap.xml', cv2.FileStorage_READ)

        self.stereoMapL_x = cv_file.getNode('stereoMapL_x').mat()
        self.stereoMapL_y = cv_file.getNode('stereoMapL_y').mat()
        self.stereoMapR_x = cv_file.getNode('stereoMapR_x').mat()
        self.stereoMapR_y = cv_file.getNode('stereoMapR_y').mat()
        self.Q = cv_file.getNode('Q').mat()

    def undistortrectify(self, frame_r, frame_l):
        undistorted_l = cv2.remap(frame_l, self.stereoMapL_x, self.stereoMapL_y, cv2.INTER_LANCZOS4,
                                  cv2.BORDER_CONSTANT, 0)
        undistorted_r = cv2.remap(frame_r, self.stereoMapR_x, self.stereoMapR_y, cv2.INTER_LANCZOS4,
                                  cv2.BORDER_CONSTANT, 0)

        # Return undistorted and rectified images
        return undistorted_r, undistorted_l
