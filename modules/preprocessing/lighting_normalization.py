# lighting_normalization.py
import numpy as np


def normalize_lighting(image, gamma):
    # Normalize the pixel values to range between 0 and 1
    image = image / 255.0

    # Apply gamma correction
    corrected_image = np.power(image, gamma)

    # Rescale back to 0-255
    return np.uint8(corrected_image * 255)
