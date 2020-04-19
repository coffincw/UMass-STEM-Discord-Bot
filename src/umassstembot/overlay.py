from PIL import Image, ImageFile, ImageDraw, ImageFont, GifImagePlugin, ImageSequence
import numpy as np
import requests
import math
import random
from io import BytesIO
import textwrap
import imageio
imageio.plugins.ffmpeg.download()
import moviepy.editor as mp
from pathlib import Path


marius_origin = (28, 428)
barr_origin = (20, 280)
tim_origin = (40, 186)
lan_origin = (13, 104)
landrew_origin = (3, 64)
shel_origin = (2, 116)
hand_origin = (2, 105)

def draw_text(text, image, image_origin):
    person_image = Image.open(image)
    font = ImageFont.truetype('fonts/PermanentMarker-Regular.ttf', size=100)                # load in font
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

    # TODO disable overlapping (1) or allow overlapping (2)?
    if image_origin == (28, 428): # if mdraw
        width = padding_side + max_line_width + person_image.width - image_origin[0]
    else:
        width = padding_side + max(last_line.width + person_image.width - image_origin[0], max_line_width + padding_side)
    height = padding_top + max(person_image.height,
                           total_text_height + ((len(lines)-1) * line_spacing_pixels)  # the actual height of the text
                           + person_image.height - image_origin[1] - last_line.height + best_hand_pos[1])
    white_background = Image.new("RGBA", (width, height) , background_fill)

    # TODO disable overlapping (1) or allow overlapping (2)?
    if image_origin == (28, 428): # if mdraw
        person_x = padding_side + max_line_width - image_origin[0]
    else:
        person_x = padding_side - image_origin[0] + last_line.width

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

#returns a list of the end of line indices
def end_of_line_indices(text):
    spaces = []
    character_limit = 30
    prev_space_index = 0
    current_index = 0
    for char in text:
        if char == ' ':
            if current_index > character_limit:
                spaces.append(prev_space_index)
                character_limit += 30
            prev_space_index = current_index
        current_index+=1
    return spaces

# returns the longest string in a list of strings
def longest_string(arr):
    long_string = 'AAAAAAAAAAAAAAA' # default smallest length
    for string in arr:
        if len(string) > len(long_string):
            long_string = string
    return long_string

def paste_text_top_bottom(top, bottom, background_image):
    image_width, image_height = background_image.size
    font_size = 1
    font = ImageFont.truetype('fonts/impact.ttf', size=font_size)                # load in font

    # find the top space indices
    top_ends = end_of_line_indices(top)

    # find the bottom space indices
    bottom_ends = end_of_line_indices(bottom)

    # break up top into lines 30 characters or less
    top_lines = []
    prev_index = 0
    for index in top_ends:
        top_lines.append(top[prev_index:index])
        prev_index = index
    top_lines.append(top[prev_index:])


    #break up bottom into lines 30 characters or less
    bottom_lines = []
    prev_index = 0
    for index in bottom_ends:
        bottom_lines.append(bottom[prev_index:index])
        prev_index = index
    bottom_lines.append(bottom[prev_index:])

    # reverse bottom lines
    bottom_lines.reverse()

    # find longest line
    longest_top = longest_string(top_lines)
    longest_bottom = longest_string(bottom_lines)
    longest_line = longest_top if len(longest_top) > len(longest_bottom) else longest_bottom

    # portion of image width you want text width to be
    img_fraction = .85

    # scale font to size of image
    while font.getsize(longest_line)[0] < img_fraction*image_width:
        font_size += 1
        font = ImageFont.truetype('fonts/impact.ttf', font_size)

    # create draw for drawing text
    draw = ImageDraw.Draw(background_image)

    # paste top lines
    line_num = 0
    for line in top_lines:
        # find coordinates of centered text
        w, h = draw.textsize(line, font=font)

        # set coordinates for the text
        x, y = (image_width-w)/2, 5+(line_num*h)

        # thin border
        draw.text((x-2, y-2), line, font=font, fill='black')
        draw.text((x+2, y-2), line, font=font, fill='black')
        draw.text((x+2, y+2), line, font=font, fill='black')
        draw.text((x-2, y+2), line, font=font, fill='black')

        #draw the text
        draw.text((x, y), line, font=font, fill='white')

        line_num +=1

    # paste bottom lines
    line_num = 0
    for line in bottom_lines:
        # find coordinates of centered text
        w, h = draw.textsize(line, font=font)

        #set coordinates for the text
        x, y = (image_width-w)/2, (image_height-int(image_width/8.2))-(line_num*h)

        # thin border
        draw.text((x-2, y-2), line, font=font, fill='black')
        draw.text((x+2, y-2), line, font=font, fill='black')
        draw.text((x+2, y+2), line, font=font, fill='black')
        draw.text((x-2, y+2), line, font=font, fill='black')

        #draw the text
        draw.text((x, y), line, font=font, fill='white')

        line_num +=1

    return background_image

def paste_in_streamer_corner(zoomer_path, image_url):

    #open the image and zoomer to paste with the Image library
    try:
        image = url_to_image(image_url)
    except:
        return 0
    zoomer = Image.open(zoomer_path)

    # resize zoomer (always want to scale down zoomer as 8X zoomer's dimensions would be too big for discord anyway)
    image_w, image_h = image.size
    zoomer.thumbnail((image_w/3, image_h/3))
    
    # get the position to paste the zoomer
    zoomer_w, zoomer_h = zoomer.size
    x_pos = int(image_w - zoomer_w - (image_h/100))
    y_pos = int((image_h/100))

    # paste zoomer on the image
    image.paste(zoomer, (x_pos, y_pos))

    return image

def url_to_image(url):
    response = requests.get(url)
    ImageFile.LOAD_TRUNCATED_IMAGES = True                                                  # needed to avoid uneeded errors caused by weird image input
    image = Image.open(BytesIO(response.content)).convert("RGBA")
    return image

# def gif_url_to_image_list(url, cmd):
#     response = requests.get(url)
#     ImageFile.LOAD_TRUNCATED_IMAGES = True
#     frameList = []
#     try:
#         gif = Image.open(BytesIO(response.content))
#     except:
#         return 0
#     for frame in ImageSequence.Iterator(gif):
#         width, height = frame.size
#         if width <= 500 and height <=500:
#             refactor_width = 500
#             ratio_percent = (refactor_width/float(width))
#             refactor_height = int((float(height)*float(ratio_percent)))
#             frame = frame.resize((refactor_width, refactor_height))
#             #resizing if the image has a tendency to be too big even for small gifs, used for high res templates
#             if cmd > 2:
#                 width, height = frame.size
#                 refactor_width = 600
#                 ratio_percent = (refactor_width/float(width))
#                 refactor_height = (int(float(height)*float(ratio_percent)))
#                 frame = frame.resize((refactor_width, refactor_height))
#         frameList.append(frame.convert("RGBA"))
#     return frameList

def get_image_url(message, index):
    image_url = ''
    try:                                                                                    # if the member attached an image with the command
        image_url = message.attachments[0].url
    except:                                                                                 # if the member used a url with the command
        extension = ['.jpg', '.png', '.jpeg']
        for ext in extension:
            if message.content.lower().endswith(ext):
                image_url = message.content[index:]
        if (image_url == ''):                                                               # if member didnt use a url or send a file
            return 0
    return image_url


def get_image_url_args(message, args, num_args, image_arg_index):
    image_url = ''
    try:                                                                                    # if the member attached an image with the command
        image_url = message.attachments[0].url
    except:                                                                                 # if the member used a url with the command
        if len(args) != num_args:
            return 0
        extension = ['.jpg', '.png', '.jpeg']
        
        for ext in extension:
            if args[image_arg_index].lower().endswith(ext):
                image_url = args[image_arg_index]
        if (image_url == ''):                                                               # if member didnt use a url or send a file
            return 0
    return image_url

