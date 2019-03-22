from PIL import Image, ImageFile
import requests
from io import BytesIO

def overlay_image(target, overlay_image):
    try:
        overlay = Image.open(overlay_image)
    except:
        return 0                                                  
    width, heigth = target.size                                                             # size of inputed image, used for scaling
    white_background = Image.new("RGBA", (width + 500, heigth + 200), (255, 255, 255))      # white background created based on the size of the inputed image
    white_background.paste(target, (0, 0), target)                                          # paste the inputed image in the upper left hand corner
    white_background.paste(overlay, (width - 450, heigth - 450), overlay)                   # paste marius at the bottom right hand corner of the inputed image
    return white_background

def url_to_image(url):
    response = requests.get(url)
    ImageFile.LOAD_TRUNCATED_IMAGES = True                                                  # needed to avoid uneeded errors caused by weird image input
    image = Image.open(BytesIO(response.content)).convert("RGBA")
    return image

def get_image_url(ctx):
    image_url = ''
    try:                                                                                    # if the member used a url with the command
        image_url = ctx.message.attachments[0]['url']
    except:                                                                                 
        extension = ['.jpg', '.png', '.jpeg']
        for ext in extension:
            if ctx.message.content.endswith(ext):
                image_url = ctx.message.content[7:]
        if (image_url == ''):                                                               # if member didnt use a url or send a file
            return 0
    return image_url
