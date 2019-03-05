from PIL import Image
import requests
from io import BytesIO

def overlay_image(background, overlay_image):
    overlay = Image.open(overlay_image) #opens the overlay image
    

    background.paste(overlay, (0, 0), overlay) #pastes the overlay image on top of the background image
    return background

def url_to_image(url):
    print("test")
    response = requests.get(url)
    print("test1")
    image = Image.open(BytesIO(response.content))
    print("test2")
    return image
