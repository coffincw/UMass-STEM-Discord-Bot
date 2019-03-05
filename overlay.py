from PIL import Image, ImageFile
import requests
from io import BytesIO

def overlay_image(target, overlay_image):
    overlay = Image.open(overlay_image) #opens the overlay image
    width, heigth = target.size
    white_background = Image.new("RGBA", (width + 500, heigth + 400), (255, 255, 255))
    #white_background = Image.open('C:/Users/Caleb/Documents/Programming-Projects/UMassMemeBot/memes/white-background.png').convert("RGBA")
    white_background.paste(target, (0, 0), target)
    white_background.paste(overlay, (width - 450, heigth - 450), overlay)
    # print("test1")
    # background.paste(overlay, (0, 0), overlay) #pastes the overlay image on top of the background image
    # print("test2")
    return white_background

def url_to_image(url):
    response = requests.get(url)
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    image = Image.open(BytesIO(response.content)).convert("RGBA")
    return image
