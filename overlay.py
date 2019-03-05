from PIL import Image, ImageFile
import requests
from io import BytesIO

def overlay_image(target, overlay_image):
    overlay = Image.open(overlay_image)                                                     #opens the overlay image
    width, heigth = target.size                                                             # size of inputed image, used for scaling
    white_background = Image.new("RGBA", (width + 500, heigth + 400), (255, 255, 255))      # white background created based on the size of the inputed image
    white_background.paste(target, (0, 0), target)                                          # paste the inputed image in the upper left hand corner
    white_background.paste(overlay, (width - 450, heigth - 450), overlay)                   # paste marius at the bottom right hand corner of the inputed image
    return white_background

def url_to_image(url):
    response = requests.get(url)
    ImageFile.LOAD_TRUNCATED_IMAGES = True                                                  # needed to avoid uneeded errors caused by weird image input
    image = Image.open(BytesIO(response.content)).convert("RGBA")
    return image
