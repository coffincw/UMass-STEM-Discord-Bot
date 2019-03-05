from PIL import Image
import requests
from io import BytesIO

def overlay_image(background, overlay_image):
    overlay = Image.open(overlay_image) #opens the overlay image
    
    print("test1")
    background.paste(overlay, (0, 0), overlay) #pastes the overlay image on top of the background image
    print("test2")
    return background

def url_to_image(url):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    return image
