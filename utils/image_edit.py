import numpy as np
from PIL import Image
import sys

def load_image(image_path):
    try:
        image = Image.open(image_path)
        return image
    except:
        print("Error loading image")
        sys.exit(1)

def negative_image(image_array):
    image_array = 255 - image_array
    return Image.fromarray(image_array)

def solarize_image(image_array, threshold=128):
    image_array = np.where(image_array < threshold, image_array, 255 - image_array)
    return Image.fromarray(image_array)

def darken_image(image_array, factor=0.5):
    image_array = (image_array * factor).clip(0, 255).astype(np.uint8)
    return Image.fromarray(image_array)

def lighten_image(image_array, factor=1.5):
    normalized_image_array = image_array / 255.0
    lightened_array = normalized_image_array * factor
    lightened_array = np.clip(lightened_array, 0.0, 1.0)
    return_array = (lightened_array * 255).astype(np.uint8)
    return Image.fromarray(return_array)

def adjust_brightness(image_array, factor=1.0):
    try:
        image_array = image_array.astype(np.float32)
        adjusted_array = image_array * factor
        adjusted_array = np.clip(adjusted_array, 0, 255).astype(np.uint8)
        return Image.fromarray(adjusted_array)
    except Exception as e:
        print(f"Error adjusting brightness: {e}")
        return None

def resize_image(image_array, new_size=(256, 256)):
    old_height, old_width, old_channels = image_array.shape
    resized_image = np.zeros((new_size[1], new_size[0], old_channels), dtype=np.uint8)

    x_ratio = old_width / new_size[0]
    y_ratio = old_height / new_size[1]

    for y in range(new_size[1]):
        for x in range(new_size[0]):
            px = int(x * x_ratio)
            py = int(y * y_ratio)
            resized_image[y, x] = image_array[py, px]
    return Image.fromarray(resized_image)

def parse_hex_color(hex_color):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        raise ValueError("Invalid hex color")
    r = int(hex_color[:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:], 16)
    return (r, g, b)

def add_border(image_array, border_size=10, color="#000000"):
    (r, g, b) = parse_hex_color(color)
    old_h, old_w, channels = image_array.shape
    new_h = old_h + border_size * 2
    new_w = old_w + border_size * 2

    new_image = np.zeros((new_h, new_w, channels), dtype=image_array.dtype)
    new_image[:, :] = [r, g, b]

    new_image[border_size:old_h + border_size, border_size:old_w + border_size] = image_array
    return Image.fromarray(new_image)
"""
def test_image_edit():

    image_path = "/home/pospim/Desktop/python/semestr/utils/star_wars.jpg"

    light_path = "/home/pospim/Desktop/python/semestr/utils/star_wars_lighten.jpg"
    dark_path = "/home/pospim/Desktop/python/semestr/utils/star_wars_darken.jpg"
    solar_path = "/home/pospim/Desktop/python/semestr/utils/star_wars_solarize.jpg"
    image = load_image(image_path)
    print(image.size)
    image_array = np.array(image)
    solarized_image = solarize_image(image_array)
    darkened_image = darken_image(image_array)
    lightened_image = lighten_image(image_array)

if __name__ == '__main__':
    test_image_edit()
    print("Image edit test passed!")
"""