import discord
import random
import os
from pathlib import Path
import overlay as over
from filters import make_draw_gif
from face_detection import paste_on_face

bot_last_command = {} #Key = User ID, Value = Bot's most recent message tied to the command

async def draw_universal(ctx, path, command_end_index, origin, name):
    """Universal function which is called by draw command with the following arguments

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
        - path: path to the drawing image (ie memes/lan/landrew.png)
        - command_end_index: index the end of the command (ie. for bdraw its 7 for '$' 'b' 'd' 'r' 'a' 'w' ' ')
        - origin: pixel origin imported from overlay.py
        - name: output file name
    """
    channel = ctx.channel
    async with channel.typing():
        url = over.get_image_url(ctx.message, command_end_index) 
        if url == 0: # no url, hand should write the inputed text 
            if len(ctx.message.content[command_end_index:].strip()) == 0:
                # no input given, try to use previous bot output 
                if bot_last_command[ctx.author.id] is not None:
                    message = bot_last_command[ctx.author.id]
                    url = over.get_image_url(message, 0)
                    output = over.overlay_image(over.url_to_image(url), Path(path), origin)
                else:
                    await channel.send(embed=discord.Embed(description="No previous bot command to pull from. Please specify text or an image.", color=discord.Color.red()))
                    return
            else:
                output = over.draw_text(ctx.message.content[command_end_index:], Path(path), origin)
        else: # url inputed, hand should draw on the image
            output = over.overlay_image(over.url_to_image(url), Path(path), origin)
        output.save(name + '.png')
        try:
            message = await channel.send(file=discord.File(name + '.png'))
        except:
            message = await channel.send(embed=discord.Embed(description="Image too large", color=discord.Color.red()))
        track_command(ctx.author.id, message) # tracks the most recent command of a user
    os.remove(name + '.png')

async def ify(ctx, scale, path, file_name, *args):
    """Command to paste a face on top of faces in an inputed image using facial recognition

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
        - args: arguments of the message
        - scale: specified scale for the faces
        - path: face image path
        - file_name: output file name
    """
    channel = ctx.channel
    async with channel.typing():
        url = over.get_image_url_args(ctx.message, args[0], 1, 0)
        if url == 0: # invalid image
            # no input given, try to use previous bot output 
            if bot_last_command[ctx.author.id] is not None:
                message = bot_last_command[ctx.author.id]
                url = over.get_image_url(message, 0)           
            else:
                await channel.send(embed=discord.Embed(description="No previous bot command to pull from. Please specify a valid image.", color=discord.Color.red()))
                return
        output = paste_on_face(Path(path), url, scale)
        # if there were no faces found then send error
        if output == 0:
            await channel.send(embed=discord.Embed(description='No faces found, please input another image', color=discord.Color.red()))
            return

        output.save(file_name)
        try:
            message = await channel.send(file=discord.File(file_name))
            track_command(ctx.author.id, message)
        except:
            await channel.send(embed=discord.Embed(description="Image too large", color=discord.Color.red()))
    os.remove(file_name)

async def zoomcam(ctx, path, file_name, *args):
    """Command to paste a a zoomer in the corner of an image

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
        - path: zoomer image path
        - file_name: output file name
        - args: arguments of the message
    """
    channel = ctx.channel
    async with channel.typing():
        url = over.get_image_url_args(ctx.message, args[0], 1, 0)
        if url == 0: # invalid image
            # no input given, try to use previous bot output 
            if bot_last_command[ctx.author.id] is not None:
                message = bot_last_command[ctx.author.id]
                url = over.get_image_url(message, 0)           
            else:
                await channel.send(embed=discord.Embed(description="No previous bot command to pull from. Please specify a valid image.", color=discord.Color.red()))
                return
        output = over.paste_in_streamer_corner(Path(path), url)

        if output == 0:
            await channel.send(embed=discord.Embed(description="Encountered issue converting image to RGBA, please try a different image", color=discord.Color.red()))
            return

        output.save(file_name)
        try:
            message = await channel.send(file=discord.File(file_name))
            track_command(ctx.author.id, message)
        except:
            await channel.send(embed=discord.Embed(description="Image too large", color=discord.Color.red()))
    os.remove(file_name)


def track_command(author, bot_message):
    """tracks the authors most recent command

        Args:
        - author: author of the message
        - bot_message: most recent message sent by the bot corresponding to the author
    """
    bot_last_command[author] = bot_message