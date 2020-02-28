from PIL import Image, ImageFile, ImageDraw, ImageFont
import numpy as np
import random
import moviepy.editor as mp
from pathlib import Path
from overlay import shel_origin, lan_origin, landrew_origin, hand_origin, barr_origin, marius_origin, tim_origin, overlay_image

def intensify_image(image, factor):
    if factor < 0:
        return 0
    pic = image.load()
    width, height = image.size                                                              # get width and height
    for x in range(width):                                                                  # iterate through x axis of pixels
        for y in range(height):                                                             # iterate through y axis of pixels
            if (pic[x,y][0] * factor) >= 255:
                pic[x,y] = (255, pic[x,y][1], pic[x,y][2])
            else:
                pic[x,y] = (int(pic[x,y][0]*factor), pic[x,y][1], pic[x,y][2])
            if (pic[x,y][1] * factor) >= 255:
                pic[x,y] = (pic[x,y][0], 255, pic[x,y][2])
            else:
                pic[x,y] = (pic[x,y][0], int(pic[x,y][1]*factor), pic[x,y][2])
            if (pic[x,y][2] * factor) >= 255:
                pic[x,y] = (pic[x,y][0], pic[x,y][1], 255)
            else:
                pic[x,y] = (pic[x,y][0], pic[x,y][1], int(pic[x,y][2]*factor))
    return image

def highlight_image(image):
    pic = image.load()
    width, height = image.size
    for x in range(width):
        for y in range(height):
            pixel1 = pic[x,y]
            pixel2 = pic[x,y]
            if x == (width-1) and y != (height-1):
                pixel2 = pic[x, y+1]
            elif x == (width-1) and y == (height-1) and height != 1:
                pixel2 = pic[x, y-1]
            elif x == (width-1) and y == (height-1) and height == 1:
                pixel2 = pic[x, y]
            else:
                pixel2 = pic[x+1, y]
            avg1 = (pixel1[0] + pixel1[1] + pixel1[2])/3
            avg2 = (pixel2[0] + pixel2[1] + pixel2[2])/3
            pixelValue = int(abs(avg1-avg2))
            pic[x,y] = (pixelValue, pixelValue, pixelValue)
    return image

def custom_edge_highlight_image(image, red, green, blue):
    if red > 255 or red < 0 or green > 255 or green < 0 or blue > 255 or blue < 0:
        return 0
    image = highlight_image(image)
    pic = image.load()
    width, height = image.size
    for x in range(width):
        for y in range(height):
            pixel = pic[x,y]
            if pixel[0] > 25 and pixel[1] > 25 and pixel[2] > 25:
                pic[x,y] = (red, green, blue)
    return image

def mirror_y(image):
    pic = image.load()
    width, height = image.size
    width = width-1
    mid = int(width/2)
    for x in range(mid):
        for y in range(height):
            pixel = pic[x,y]
            pic[width-x, y] = pixel
    return image

def mirror_x(image):
    pic = image.load()
    width, height = image.size
    mid = int(height/2)
    height = height-1
    for x in range(width):
        for y in range(mid):
            pixel = pic[x,y]
            pic[x, height-y] = pixel
    return image

def scramble_pixels(image):
    pic = image.load()
    width, height = image.size
    for x in range(width):
        for y in range(height):
            randFactor = random.uniform(0, 1)
            pixel = pic[x,y]
            red = int(pixel[0]*randFactor)
            green = int(pixel[1]*randFactor)
            blue = int(pixel[2]*randFactor)
            pic[x,y] = (red, green, blue)
    return intensify_image(image, 2)

def pixelate_image(image, factor):
    factor = int(factor)
    pic = image.load()
    width, height = image.size
    for x in range(0, width, factor):
        for y in range(0, height, factor):
            pixel = pic[x,y]
            red = pixel[0]
            green = pixel[1]
            blue = pixel[2]
            for x2 in range(x, (x+factor), 1):
                if x2 >= width:
                    break
                for y2 in range(y, (y+factor), 1):
                    if y2 >= height:
                        break
                    pic[x2, y2] = (red, green, blue)
    return image

def saturate_image(image, factor):
    pic = image.load()
    width, height = image.size
    for x in range(width):
        for y in range(height):
            pixel = pic[x,y]
            red = pixel[0]
            green = pixel[1]
            blue = pixel[2]
            maxVal = max((red, green, blue)) #dumb pixels have a 4th alpha value of 255 so that's always considered max if you don't do this, which breaks the code
            if red == maxVal:
                red = int(red * factor)
                if red > 255:
                    red = 255
            elif green == maxVal:
                green = int(green*factor)
                if green > 255:
                    green = 255
            elif blue == maxVal:
                blue = int(blue*factor)
                if blue > 255:
                    blue = 255
            pic[x,y] = (red, green, blue)
    return image

def make_okay_clip(image):
    imageArr = np.array(image)
    clip = mp.ImageClip(imageArr)
    clip = clip.set_duration(1.5, change_end=True)
    return clip

def make_draw_gif(frameList, num):
    imageClipLists = []
    frameLength = 1.0/24.0
    for frame in frameList:
        if num == 0:
            frame = overlay_image(frame, Path("../memes/barrington/bdraw.png"), barr_origin)
        elif num == 1:
            frame = overlay_image(frame, Path("../memes/marius/draw.png"), marius_origin)
        elif num == 2:
            frame = overlay_image(frame, Path("../memes/tim/tdraw.png"), tim_origin)
        elif num == 3:
            frame = overlay_image(frame, Path("../memes/sheldraw.png"), shel_origin)
        elif num == 4:
            frame = overlay_image(frame, Path("../memes/lan/lan-draw.png"), lan_origin)
        elif num == 5:
            frame = overlay_image(frame, Path("../memes/hand.png"), hand_origin)
        elif num == 6:
            frame = overlay_image(frame, Path("../memes/lan/landrew.png"), landrew_origin)
        arr = np.array(frame)
        clip = mp.ImageClip(arr)
        clip = clip.set_duration(frameLength)
        imageClipLists.append(clip)
    #print(imageClipLists)
    concatClip = mp.concatenate_videoclips(imageClipLists, method="compose")
    return concatClip