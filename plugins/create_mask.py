import os, time

from PIL import Image
import PIL.ImageOps
import numpy as np

from keras.optimizers import Adam
from metrics import dice_coef, dice_coef_loss, numpy_dice
from skimage.transform import resize
from skimage.exposure import equalize_adapthist, equalize_hist

from models import actual_unet, simple_unet

IMAGE_SIZE = 400
IMG_ROWS = 96
IMG_COLS = 96
CURRENT_IMG = 'current_image.png'
WEIGHTS_FILE = 'weights.h5'

def convert_np_mask_to_image(np_predicted_mask):
    squeezed = np.squeeze(np_predicted_mask, axis=0)
    squeezed = np.squeeze(squeezed, axis=2)
    img = Image.fromarray(squeezed).convert('RGBA')
    img = inverse_colors(img)
    width_percent = (IMAGE_SIZE / float(img.size[0]))
    height_size = int((float(img.size[1])*float(width_percent)))
    img = img.resize((IMAGE_SIZE, height_size))

    pixel_data = img.load()
    width, height = img.size

    for y in range(height):
        for x in range(width):
            if pixel_data[x, y] == (255, 255, 255, 255):
                pixel_data[x, y] = (0, 0, 0, 0)
            else:
                pixel_data[x, y] = (255, 0, 0, 127)

    img.save('current_mask.png', "PNG")


def inverse_colors(image):
    r,g,b,a = image.split()
    rgb_image = Image.merge('RGB', (r,g,b))

    inverted_image = PIL.ImageOps.invert(rgb_image)

    r2,g2,b2 = inverted_image.split()

    final_transparent_image = Image.merge('RGBA', (r2,g2,b2,a))

    final_transparent_image.save('new_file.png')
    return final_transparent_image


def normalize_image(np_image):
    img = equalize_hist(np_image)
    img = resize(img, (IMG_ROWS, IMG_COLS), preserve_range=True)
    return img


def predict_mask(np_image):
    normalized_img = normalize_image(np_image)

    # Expanding dims to match expected by model
    new_img = np.expand_dims(normalized_img, axis=0)
    new_img = np.expand_dims(new_img, axis=3)

    model = simple_unet(IMG_ROWS, IMG_COLS)
    model.load_weights(WEIGHTS_FILE)
    model.compile(optimizer=Adam(), loss=dice_coef_loss, metrics=[dice_coef, 'binary_accuracy'])
    np_predicted_mask = model.predict(new_img, verbose=1)

    convert_np_mask_to_image(np_predicted_mask)


if __name__ == '__main__':
    last_date = os.stat(CURRENT_IMG)[8]
    while True:
        try:
            modification_date = os.stat(CURRENT_IMG)[8]
            if modification_date != last_date:
                im_frame = Image.open(CURRENT_IMG)
                np_frame = np.array(im_frame)

                predict_mask(np_frame)
                last_date = modification_date
        except OSError:
            pass

        time.sleep(0.1)
