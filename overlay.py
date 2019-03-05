from PIL import Image
import requests
from io import BytesIO

def overlay_image(background, overlay_image):
    overlay = Image.open(overlay_image) #opens the overlay image
    white_background = Image.open('C:/Users/Caleb/Documents/Programming-Projects/UMassMemeBot/memes/white-background.png').convert("RGBA")
    size = 1440, 810
    print("testing")
    try:
        background.thumbnail(size)
    except:
        print("Too small")
        return 0
    white_background.paste(background, (0, 0), background)
    white_background.paste(overlay, (800, 250), overlay)
    # print("test1")
    # background.paste(overlay, (0, 0), overlay) #pastes the overlay image on top of the background image
    # print("test2")
    return white_background

def url_to_image(url):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content)).convert("RGBA")
    return image
