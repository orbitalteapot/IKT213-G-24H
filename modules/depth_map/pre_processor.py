# preprocessing.py
import cv2 as cv
import json
import os
from modules.preprocessing import reduce_noise, normalize_lighting, enhance_contrast


class Preprocessor:
    def __init__(self, window_name='Preprocessing', config_file='./modules/depth_map/preprocess_params.json'):
        self.window_name = window_name
        self.config_file = config_file
        self.params = {'NOISE_THRESHOLD': 0, 'GAMMA': 1.0, 'CONTRAST_LEVEL': 1.0, }
        self.scaling_factors = {'NOISE_THRESHOLD': 100, 'GAMMA': 100, 'CONTRAST_LEVEL': 100, }
        self.max_values = {'NOISE_THRESHOLD': 1000,  # Adjust as needed
            'GAMMA': 500, 'CONTRAST_LEVEL': 500, }
        self.load_parameters()
        self.create_trackbars()

    def load_parameters(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as file:
                self.params.update(json.load(file))

    def save_parameters(self):
        with open(self.config_file, 'w') as file:
            json.dump(self.params, file, indent=4)

    def create_trackbars(self):
        cv.namedWindow(self.window_name)
        for param in self.params:
            initial_value = int(self.params[param] * self.scaling_factors[param])
            cv.createTrackbar(param, self.window_name, initial_value, self.max_values[param],
                              lambda val, p=param: self.on_trackbar_change(p, val))

    def on_trackbar_change(self, param, val):
        self.params[param] = val / self.scaling_factors[param]

    def preprocess(self, image):
        image = reduce_noise(image, self.params['NOISE_THRESHOLD'])
        image = normalize_lighting(image, self.params['GAMMA'])
        image = enhance_contrast(image, self.params['CONTRAST_LEVEL'])
        return image
