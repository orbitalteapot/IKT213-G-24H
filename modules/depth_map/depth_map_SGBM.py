import cv2 as cv
import numpy as np
import os
import json
from modules.edge_detection.stereo_vision import StereoVision


class DepthMapProcessorSGBM:
    def __init__(self, window_name='Depth Map', config_file='./modules/depth_map/depth_map_params.json',
                 q_file_path='Q.xml'):
        self.window_name = window_name
        self.config_file = config_file
        self.q_file_path = q_file_path
        self.autotune_max = -10000000
        self.autotune_min = 10000000
        self.stereo_vision = StereoVision()
        self.params = {'numDisparities': 6,  # Multiplier for 16
            'blockSize': 5,  # Must be odd and at least 5
            'minDisparity': 0, 'uniquenessRatio': 10, 'speckleWindowSize': 100, 'speckleRange': 2, 'preFilterCap': 25,
            'P1': 600,  # Smoothness term for SGBM
            'P2': 2400,  # Larger smoothness term for SGBM
            'disp12MaxDiff': 1, }
        self.max_values = {'numDisparities': 10,  # Max multiplier (numDisparities = multiplier * 16)
            'blockSize': 25,  # Max value for (blockSize - 5) // 2
            'uniquenessRatio': 100, 'speckleWindowSize': 200, 'speckleRange': 32, 'preFilterCap': 63, 'P1': 1000,
            'P2': 4000, 'disp12MaxDiff': 25}
        self.load_parameters()
        self.create_trackbars()
        self.Q = self.load_q_matrix(self.q_file_path)

    # Load Q matrix from file (provided by stereo calibration) to reproject disparity to 3D points
    def load_q_matrix(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Q matrix file not found at {file_path}")

        cv_file = cv.FileStorage(file_path, cv.FILE_STORAGE_READ)
        Q = cv_file.getNode("Q").mat()
        cv_file.release()

        if Q is None:
            raise ValueError("Q matrix could not be loaded from file.")

        return Q

    #  Load parameters from a JSON file
    def load_parameters(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as file:
                self.params.update(json.load(file))

    # Save parameters to a JSON file
    def save_parameters(self):
        with open(self.config_file, 'w') as file:
            json.dump(self.params, file, indent=4)

    # Create trackbars for each parameter
    def create_trackbars(self):
        cv.namedWindow(self.window_name)
        for param, value in self.params.items():
            cv.createTrackbar(param, self.window_name, value, self.max_values.get(param, 100),
                              lambda val, p=param: self.on_trackbar_change(p, val))

    # Callback function for trackbar change
    def on_trackbar_change(self, param, val):
        self.params[param] = val

    # Get parameter value
    def get_param(self, param, default=None):
        return self.params.get(param, default)

    # Create StereoSGBM matcher with the current parameters
    def create_stereo_matcher(self):
        # Configure parameters for StereoSGBM
        numDisparities = self.params['numDisparities'] * 16  # Must be multiple of 16
        blockSize = self.params['blockSize'] * 2 + 5  # Ensures odd number >= 5
        minDisparity = self.params['minDisparity']
        uniquenessRatio = self.params['uniquenessRatio']
        speckleWindowSize = self.params['speckleWindowSize']
        speckleRange = self.params['speckleRange']
        preFilterCap = self.params['preFilterCap']
        disp12MaxDiff = self.params['disp12MaxDiff']
        P1 = self.params['P1']
        P2 = self.params['P2']

        # Create StereoSGBM matcher
        stereo = cv.StereoSGBM_create(minDisparity=minDisparity, numDisparities=numDisparities, blockSize=blockSize,
            P1=P1, P2=P2, disp12MaxDiff=disp12MaxDiff, uniquenessRatio=uniquenessRatio,
            speckleWindowSize=speckleWindowSize, speckleRange=speckleRange, preFilterCap=preFilterCap,
            mode=cv.STEREO_SGBM_MODE_SGBM_3WAY)
        return stereo

    # Compute disparity map and extract height information
    def compute_disparity_map(self, left_image, right_image, zone1=40, zone2=200, zone3=400, min_distance=0,
                              max_distance=5000, disparity_threshold=1.0):
        # Ensure images are grayscale (required for SGBM)
        if left_image.ndim == 3:
            left_image = cv.cvtColor(left_image, cv.COLOR_BGR2GRAY)
        if right_image.ndim == 3:
            right_image = cv.cvtColor(right_image, cv.COLOR_BGR2GRAY)

        self.stereo = self.create_stereo_matcher()

        # Compute disparity map
        disparity = self.stereo.compute(left_image, right_image).astype(np.float32) / 16.0

        # Normalize disparity for visualization
        min_disp, max_disp = cv.minMaxLoc(disparity)[:2]
        disparity_visual = cv.convertScaleAbs(disparity, alpha=255 / (max_disp - min_disp),
                                              beta=-min_disp * (255 / (max_disp - min_disp)))

        # Create an object mask based on the disparity threshold
        object_mask = (disparity > disparity_threshold) & (disparity_visual > 0)

        # Reproject disparity to 3D points
        points_3D = cv.reprojectImageTo3D(disparity, self.Q, ddepth=cv.CV_32F)

        # Compute distances from the camera to each point
        distances = np.linalg.norm(points_3D, axis=2)

        # Create zones for height computation
        zones = [zone1, zone2, zone3]

        # Set default average heights to NaN to indicate no data
        avg_heights = [np.nan, np.nan, np.nan]

        # For each zone (specified row), compute the average distance
        for idx, zone_row in enumerate(zones):
            # Ensure the zone_row is within the image bounds
            if zone_row < 0 or zone_row >= distances.shape[0]:
                continue  # Skip if the row index is out of bounds

            # Get the object_mask and distances at the specified row
            object_mask_row = object_mask[zone_row, :]
            distances_row = distances[zone_row, :]

            # Filter distances where object_mask is True and distances are within min and max
            valid_distances = distances_row[object_mask_row]
            valid_distances = valid_distances[
                np.isfinite(valid_distances) & (valid_distances >= min_distance) & (valid_distances <= max_distance)]

            # Compute average distance
            avg_distance = valid_distances.mean() if valid_distances.size > 0 else np.nan

            # Assign the average distance to the corresponding variable
            avg_heights[idx] = avg_distance

        # Assign the average distance to the corresponding variable
        avg_height1, avg_height2, avg_height3 = avg_heights

        # Apply color map for visualization
        depth_visual_colormap = cv.applyColorMap(disparity_visual, cv.COLORMAP_JET)

        # Overlay zones and average heights on the depth map
        depth_visual_colormap = self.overlay_zones(depth_visual_colormap, zones, avg_heights)

        # Overlay parameters on the depth map
        output_image = self.overlay_parameters(depth_visual_colormap)
        
        # Return the output image, average heights for each zone
        return output_image, avg_height1, avg_height2, avg_height3


    # Overlay zones and average heights on the depth map
    def overlay_zones(self, image, zones, avg_heights):
        for idx, zone_row in enumerate(zones):
            if 0 <= zone_row < image.shape[0]:
                # Draw the zone line
                cv.line(image, (0, zone_row), (image.shape[1], zone_row), (0, 255, 0), 1)
                # Prepare the text to display
                avg_distance = avg_heights[idx]
                if np.isnan(avg_distance):
                    text = "No data"
                else:
                    text = f"Height: {avg_distance:.2f}"
                # Determine text position (a bit above the line)
                text_position = (10, max(0, zone_row - 10))
                # Put the text on the image
                cv.putText(image, text, text_position, cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        return image

    # Overlay parameters on the depth map
    def overlay_parameters(self, image):
        param_image = np.zeros((image.shape[0], 200, 3), dtype=np.uint8)
        y = 20
        for param, value in self.params.items():
            value_display = value * 16 if param == 'numDisparities' else value
            text = f"{param}: {value_display}"
            cv.putText(param_image, text, (10, y), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y += 20
        combined_image = np.hstack((param_image, image))
        return combined_image
