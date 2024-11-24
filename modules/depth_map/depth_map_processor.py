# depth_map_processor.py
import cv2 as cv
import numpy as np
from modules.edge_detection.stereo_vision import StereoVision


class DepthMapProcessor:
    def __init__(self, window_name='Depth Map'):
        self.window_name = window_name
        self.stereo_vision = StereoVision()
        self.params = {'numDisparities': 32,  # Multiplier for 16
            'blockSize': 5,  # Adjusted in code to be odd and at least 5
            'minDisparity': 0, 'textureThreshold': 0, 'uniquenessRatio': 15, 'speckleWindowSize': 0, 'speckleRange': 2,
            'disp12MaxDiff': 1}
        self.max_values = {'numDisparities': 10,  # Max multiplier (numDisparities = multiplier * 16)
            'blockSize': 25,  # Max value for (blockSize - 5) // 2
            'uniquenessRatio': 100, 'speckleWindowSize': 200, 'speckleRange': 10, 'disp12MaxDiff': 25,
            'textureThreshold': 100}
        self.create_trackbars()

    def create_trackbars(self):
        cv.namedWindow(self.window_name)
        for param, value in self.params.items():
            cv.createTrackbar(param, self.window_name, value, self.max_values.get(param, 100),
                              lambda val, p=param: self.on_trackbar_change(p, val))

    def on_trackbar_change(self, param, val):
        self.params[param] = val

    def get_param(self, param, default=None):
        return self.params.get(param, default)

    def compute_depth_map(self, left_image, right_image):
        # Process the stereo images and return a depth map with overlays
        depth_map = self.stereo_vision.process(left_image, right_image, self)
        output_image = self.overlay_parameters(depth_map)
        return output_image

    def overlay_parameters(self, image):
        # Convert the depth map (grayscale) to a 3-channel image to match param_image's dimensions
        if len(image.shape) == 2:  # Check if the image is single-channel
            image = cv.cvtColor(image, cv.COLOR_GRAY2BGR)

        param_image = np.zeros((image.shape[0], 200, 3), dtype=np.uint8)
        y = 20
        for param, value in self.params.items():
            value_display = value * 16 if param == 'numDisparities' else value
            text = f"{param}: {value_display}"
            cv.putText(param_image, text, (10, y), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y += 20

        # Now param_image and image both have 3 channels
        combined_image = np.hstack((param_image, image))
        return combined_image
