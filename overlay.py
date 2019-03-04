from PIL import Image


def overlay(background_image, overlay_image):
    background = Image.open(background_image)
    overlay = Image.open(overlay_image)

    background.paste(overlay, (0, 0), overlay)
    return background
