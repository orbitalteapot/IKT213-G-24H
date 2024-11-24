# stereo_vision.py
import cv2 as cv
import numpy as np


class StereoVision:
    def __init__(self):
        self.stereo = None  # Initialize stereo matcher only when needed

    def update_stereo_matcher(self, param_manager):
        # Retrieve updated depth map parameters from param_manager
        num_disparities = int(param_manager.get_param("numDisparities") * 16)
        block_size = int(param_manager.get_param("blockSize") * 2 + 5)
        min_disparity = int(param_manager.get_param("minDisparity", default=0))
        texture_threshold = int(param_manager.get_param("textureThreshold", default=0))
        uniqueness_ratio = int(param_manager.get_param("uniquenessRatio", default=15))
        speckle_window_size = int(param_manager.get_param("speckleWindowSize", default=0))
        speckle_range = int(param_manager.get_param("speckleRange", default=2))
        disp12_max_diff = int(param_manager.get_param("disp12MaxDiff", default=1))

        # Configure and apply stereo depth map generation with updated parameters
        self.stereo = cv.StereoBM_create(numDisparities=num_disparities, blockSize=block_size)
        self.stereo.setMinDisparity(min_disparity)
        self.stereo.setTextureThreshold(texture_threshold)
        self.stereo.setUniquenessRatio(uniqueness_ratio)
        self.stereo.setSpeckleWindowSize(speckle_window_size)
        self.stereo.setSpeckleRange(speckle_range)
        self.stereo.setDisp12MaxDiff(disp12_max_diff)

    def process(self, left_frame, right_frame, param_manager):
        # Ensure stereo matcher is updated with current parameters
        self.update_stereo_matcher(param_manager)

        # Compute disparity map
        disparity = self.stereo.compute(left_frame, right_frame)

        min = disparity.min()
        max = disparity.max()
        disparity = np.uint8(255 * (disparity - min) / (max - min))

        # Normalize the disparity map for display
        # disparity_normalized = cv.normalize(disparity, None, alpha=0, beta=255, norm_type=cv.NORM_MINMAX)
        # disparity_normalized = np.uint8(disparity_normalized)

        # Apply a color map to the normalized disparity map
        # disparity_colormap = cv.applyColorMap(disparity_normalized, cv.COLORMAP_JET)

        return disparity
