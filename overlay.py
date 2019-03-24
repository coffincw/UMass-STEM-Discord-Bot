from PIL import Image, ImageFile, ImageDraw, ImageFont
import requests
from io import BytesIO

def draw_text(text, image):
    person_image = Image.open(image)
    lines = text.split('|')
    largest_line = 0
    largest_line_capitals = 0
    for line in lines:
        if len(line) > largest_line:
            largest_line = len(line)
            for char in line:
                if char.isupper():
                    largest_line_capitals += 1
    if largest_line < 15:
        largest_line = 15
    line_height = len(lines)
    if line_height < 3:
        line_height = 3
    (width, height) = ((largest_line * 55) + (largest_line_capitals * 30) + 400, (line_height * 150)+ 200)
    white_background = Image.new("RGBA", (width, height) , (255, 255, 255))
    white_background.paste(person_image, (width -1000, height - 600), person_image)

    draw = ImageDraw.Draw(white_background) # create the drawing context

    font = ImageFont.truetype('fonts/PermanentMarker-Regular.ttf', size=100)
    #font = ImageFont.load_default()
    #font = ImageFont.load("Elephant.pil")

    # starting position
    (x, y) = (50, 50)

    color='rgb(0, 0, 0)' #black

    lines = text.split('|')

    offset = 0
    for line in lines:
        draw.text((x, y + offset), line, fill=color, font=font)
        offset += 150
    
    return white_background
    
    

    
    


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
