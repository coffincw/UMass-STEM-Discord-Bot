from PIL import Image, ImageFile, ImageDraw, ImageFont
import requests
from io import BytesIO

def draw_text(text, image):
    person_image = Image.open(image)
    font = ImageFont.truetype('fonts/PermanentMarker-Regular.ttf', size=100)                # load in font
    lines = text.split('|')                                                                 # new line every time the user includes a |
    largest_line = ''
    for line in lines:                                                                      # used for scaling the size of the text space
        if len(line) > len(largest_line):
            largest_line = line
    line_height = len(lines)
    if line_height < 3:                                                                     # set minimum height
        line_height = 3
    (width, height) = (line_size(font, largest_line) + 475, (line_height * 150)+ 200)
    white_background = Image.new("RGBA", (width, height) , (255, 255, 255))
    white_background.paste(person_image, (width -1000, height - 600), person_image)

    draw = ImageDraw.Draw(white_background)                                                 # create the drawing context

    (x, y) = (50, 50)                                                                       # starting position

    color='rgb(0, 0, 0)'                                                                    # black

    offset = 0
    for line in lines:                                                                      # iterate through lines and draw them on the white background
        draw.text((x, y + offset), line, fill=color, font=font)
        offset += 150                                                                       # increments offset so that the text isnt drawn on top of the previous line
    
    return white_background
    
def line_size(font, line):
    width = 0
    for c in line:
        width += font.getsize(c)[0]
    if width < 15:
        width = 15
    return width

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
