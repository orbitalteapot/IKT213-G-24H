# contrast_enhancement.py
import cv2 as cv


def enhance_contrast(image, level):
    # Check if the image is grayscale
    if len(image.shape) == 2:  # Grayscale image
        # Apply CLAHE directly to the grayscale image
        clahe = cv.createCLAHE(clipLimit=level, tileGridSize=(8, 8))
        enhanced_image = clahe.apply(image)
    else:  # Color (BGR) image
        # Convert to LAB color space
        lab = cv.cvtColor(image, cv.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv.split(lab)

        # Apply CLAHE to the L-channel (brightness)
        clahe = cv.createCLAHE(clipLimit=level, tileGridSize=(8, 8))
        enhanced_l_channel = clahe.apply(l_channel)

        # Merge the channels back and convert to BGR
        enhanced_lab = cv.merge((enhanced_l_channel, a_channel, b_channel))
        enhanced_image = cv.cvtColor(enhanced_lab, cv.COLOR_LAB2BGR)

    return enhanced_image
