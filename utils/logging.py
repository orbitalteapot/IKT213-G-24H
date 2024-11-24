# logging.py
from PIL import Image, ImageDraw, ImageFont


def create_logging_image(preprocessed_images, depth_image, depth_params):
    import cv2 as cv
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np

    images_height, images_width, channels = preprocessed_images[0]['image1'].shape
    padding = 10
    text_height = 30

    # Append depth image to preprocessed_images
    preprocessed_images.append({'image1': depth_image, 'image2': None,  # No second image for depth map
        'params': depth_params})

    total_steps = len(preprocessed_images)  # Including depth image

    canvas_width = total_steps * (images_width + padding) + padding
    canvas_height = 2 * images_height + text_height + 3 * padding

    # Creating a blank white canvas
    canvas = Image.new('RGB', (canvas_width, canvas_height), color=(255, 255, 255))

    # Paste each preprocessed image onto the canvas with parameters below
    for i, step_data in enumerate(preprocessed_images):
        x_pos = padding + i * (images_width + padding)
        y_pos_image1 = padding
        y_pos_image2 = y_pos_image1 + images_height + padding

        # Get images and params
        image1 = Image.fromarray(cv.cvtColor(step_data['image1'], cv.COLOR_BGR2RGB))
        image2 = step_data['image2']
        if image2 is not None:
            image2 = Image.fromarray(cv.cvtColor(image2, cv.COLOR_BGR2RGB))
        params = step_data['params']

        # Paste images onto the canvas
        canvas.paste(image1, (x_pos, y_pos_image1))
        if image2 is not None:
            canvas.paste(image2, (x_pos, y_pos_image2))

        # Add text below the images
        draw = ImageDraw.Draw(canvas)
        if image2 is not None:
            text_y_pos = y_pos_image2 + images_height + 5
        else:
            text_y_pos = y_pos_image1 + images_height + 5
        text_position = (x_pos, text_y_pos)
        draw.text(text_position, params, fill=(0, 0, 0), font_size=24)

    # Save or display the canvas
    canvas.save("composite_image.jpg")
    canvas.show()
