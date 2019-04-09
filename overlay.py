from PIL import Image, ImageFile, ImageDraw, ImageFont
import requests
from io import BytesIO
import textwrap

marius_origin = (28, 428)
barr_origin = (20, 280)
tim_origin = (40, 186)

def draw_text(text, image, image_origin):
    person_image = Image.open(image)
    font = ImageFont.truetype('fonts/BrownBagLunch.ttf', size=100)                          # load in font
    lines = text.split('|')                                                                 # new line every time the user includes a |
    line_spacing = -0.1                                                                     # as a percentage of the line height
    text_fill = (0, 0, 0)                                                                   # RGB text color
    background_fill = (255, 255, 255)                                                       # RGB background color
    characters_per_line = 120                                                               # 0 for no limit
    padding_top = 10
    padding_side = 20

    if characters_per_line > 0:
        i = 0
        while i < len(lines):
            wrapped = textwrap.wrap(lines[i], characters_per_line)
            lines.pop(i)
            for l in reversed(wrapped):
                lines.insert(i, l)
            i += len(wrapped)

    # render each line of text as an image
    line_sizes = []
    max_line_width = None
    total_text_height = 0
    for line in lines:
        if not line:  # skip empty lines
            continue

        s = font.getsize(line)

        if not max_line_width or s[0] > max_line_width:
            max_line_width = s[0]
        total_text_height += s[1]
        line_sizes.append(s)
    line_spacing_pixels = int((total_text_height / len(lines)) * line_spacing)

    last_line = render_line(font, lines[-1], text_fill, background_fill)

    # find the best position (as an offset from the bottom-right corner of the last line of text) to place the image
    best_hand_pos = None
    for x in range(last_line.width - 1, -1, -1):
        for y in range(last_line.height):
            if last_line.getpixel((x, y)) == text_fill:
                best_hand_pos = x, y
                break
        else:
            continue
        break

    # TODO allow overlapping (1) or disable overlapping (2)?
    if image_origin != (30, 428): # if not mdraw
        width = padding_side + max(last_line.width + person_image.width - image_origin[0], max_line_width + padding_side)
    else:
        width = padding_side + max_line_width + person_image.width - image_origin[0]
    height = padding_top + max(person_image.height,
                           total_text_height + ((len(lines)-1) * line_spacing_pixels)  # the actual height of the text
                           + person_image.height - image_origin[1] - last_line.height + best_hand_pos[1])
    white_background = Image.new("RGBA", (width, height) , background_fill)

    # TODO allow overlapping (1) or disable overlapping (2)?
    if image_origin != (30, 428): # if not mdraw
        person_x = padding_side - image_origin[0] + last_line.width
    else:
        person_x = padding_side + max_line_width - image_origin[0]
    person_y = height - person_image.height

    # keep track of offsets for the bottom right corner of the next line of text to draw
    offset_x = padding_side + max_line_width
    offset_y = person_y + image_origin[1] + last_line.height - best_hand_pos[1]

    # paste the last line of text, since we already rendered it
    white_background.paste(last_line, (offset_x - max_line_width, offset_y - last_line.height))
    offset_y -= last_line.height + line_spacing_pixels

    # create drawing context and draw the rest of the lines on the image
    draw = ImageDraw.Draw(white_background)
    for i in range(len(lines) - 2, -1, -1):
        draw.text((offset_x - max_line_width, offset_y - line_sizes[i][1]), lines[i], fill=text_fill, font=font)
        # increment offset so that the text isn't drawn on top of the previous line
        offset_y -= line_sizes[i][1] + line_spacing_pixels

    white_background.paste(person_image, (person_x, person_y), person_image)

    return white_background

def render_line(font, line, fill, background):
    render = Image.new('RGB', font.getsize(line), background)
    draw = ImageDraw.Draw(render)
    draw.text((0, 0), line, fill=fill, font=font)
    return render

def overlay_image(target, overlay_image, overlay_origin):
    padding_top = 10                                                                        # used when images are too short
    try:
        overlay = Image.open(overlay_image)
    except:
        return 0

    # white background created based on the size of the inputted image
    width = target.width + overlay.width - overlay_origin[0]
    height = max(target.height + overlay.height - overlay_origin[1], overlay.height + padding_top)
    white_background = Image.new("RGBA", (width, height), (255, 255, 255))

    # paste the target onto the background (coords calculated as a function of overlay position)
    target_x = width - overlay.width + overlay_origin[0] - target.width
    target_y = height - overlay.height + overlay_origin[1] - target.height
    white_background.paste(target, (target_x, target_y), target)

    # paste the overlay onto the background
    white_background.paste(overlay, (width - overlay.width, height - overlay.height), overlay)
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
