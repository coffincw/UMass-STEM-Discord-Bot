import random
from io import BytesIO
from pathlib import Path
import discord
from discord import Game
from discord.ext.commands import Bot
import asyncio
import imageio
imageio.plugins.ffmpeg.download()
import moviepy.editor as mp
from overlay import overlay_image, get_gif_url, gif_url_to_image_list, url_to_image, get_image_url, get_image_url_args, draw_text, paste_text_top_bottom, marius_origin, barr_origin, tim_origin, lan_origin, shel_origin, landrew_origin, hand_origin
from filters import intensify_image, highlight_image, custom_edge_highlight_image, mirror_x, mirror_y, scramble_pixels, pixelate_image, saturate_image, make_okay_clip, make_draw_gif
from stem_roles import stem_add_role, stem_remove_role, list_roles, list_my_roles
from face_detection import paste_on_face, open_image_cv, barr_scale, sp_scale, mar_scale, tim_scale, c_scale
import os
import random
import time

BOT_PREFIX = "$"
BOT_TOKEN = os.environ.get('BOT_TOKEN')
BOT_ROLE = "bots"

bot_last_command = {} #Key = User ID, Value = Bot's most recent message tied to the command

client = Bot(command_prefix=BOT_PREFIX)
client.remove_command('help')

@client.event
async def on_ready():
    """This function runs when the bot is started"""
    await client.change_presence(game = discord.Game(name = '#rules | $help'))
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_member_join(member):
    if member.server.id == '387465995176116224':
        welcome_channel = client.get_channel('387465995176116226') # introductions

        num_members = len(set(client.get_all_members()))

        # used to randomly pick one of the available drawing professors
        professor_chosen = random.randint(0, 6)

        welcome_message = 'Welcome ' + member.display_name + '!|You are member ' + str(num_members) + '!|To see all the channels set your major|and housing roles in #role-assignment!'
        if professor_chosen == 0:
            output = draw_text(welcome_message, Path('memes/barrington/bdraw.png'), barr_origin)
        elif professor_chosen == 1:
            output = draw_text(welcome_message, Path('memes/marius/draw.png'), marius_origin)
        elif professor_chosen == 2:
            output = draw_text(welcome_message, Path('memes/tim/tdraw.png'), tim_origin)
        elif professor_chosen == 3:
            output = draw_text(welcome_message, Path('memes/lan/lan-draw.png'), lan_origin)
        elif professor_chosen == 4:
            output = draw_text(welcome_message, Path('memes/lan/landrew.png'), landrew_origin)
        else:
            output = draw_text(welcome_message, Path('memes/sheldraw.png'), shel_origin)
        name = 'welcome-' + member.display_name + '.png'
        output.save(name)
        await client.send_file(welcome_channel, name, content=member.mention)
        os.remove(name)

@client.event
async def on_message_delete(message):
    """This function runs whenever a message is deleted

       Args:
        - message: context of the deleted message (used to get the message contents)
    """
    author = message.author
    if message.server.id == '387465995176116224':
        if (BOT_ROLE not in [role.name.lower() for role in author.roles]) and author.id != '98138045173227520':
            content = message.content
            await client.send_message(client.get_channel('557002016782680076'), '_Deleted Message_\n**Message sent by:** ' + author.mention + '\n**Channel:** ' + message.channel.mention + '\n**Contents:** *' + content + '*\n--------------')

@client.event
async def on_message_edit(before, after):
    """This function runs whenever a message is edited

       Args:
        - before: context before the edit (use to get the message contents before the message was edited)
        - after: context after the edit (use to get the message contents after the message was edited)
    """
    author = before.author
    if before.server.id == '387465995176116224': # UMass STEM Discord server ID
        if (BOT_ROLE not in [role.name.lower() for role in author.roles]) and author.id != '98138045173227520':
            before_content = before.content
            after_content = after.content
            await client.send_message(client.get_channel('557002016782680076'), '_Edited Message_\n**Message sent by:** ' + author.mention + '\n**Channel:** ' + before.channel.mention + '\n**Pre-edit contents:** *' + before_content + '*\n**Post-edit contents:** *'+ after_content + '*\n--------------')

@client.command(name='help')
async def help():
    """help command

       Output: list of accessible commands and their descriptions
    """
    embed = discord.Embed(
        color = discord.Color.orange()
    )
    # role command dictionary
    ROLE_COMMANDS = {
        '*$getlist*': 'Sends a list of all the available roles',
        '*$get [role]*': 'Gives you the specified role',
        '*$remove [role]*': 'Removes the specified role from you',
        '*$members*': 'Prints out the number of people on the server'
    }
    MEME_COMMANDS = {
        '*$mdraw [image/url/text]*': 'Sends a photo of marius drawing the specified image or text or gif, keep in mind that discord\'s gif size restrictions are a bit harsh',
        '*$tdraw [image/url/text]*': 'Sends a photo of tim drawing the specified image or text or gif, keep in mind that discord\'s gif size restrictions are a bit harsh',
        '*$bdraw [image/url/text]*': 'Sends a photo of barrington drawing the specified image or text or gif, keep in mind that discord\'s gif size restrictions are a bit harsh',
        '*$ldraw [image/url/text]*': 'Sends a photo of lan drawing the specified image or text or gif, keep in mind that discord\'s gif size restrictions are a bit harsh',
        '*$landrew [image/url/text]*': 'Sends a photo of a different occasion of lan drawing the specified image or text, keep in mind that discord\'s gif size restrictions are a bit harsh',
        '*$shelpoint [image/url/text]*': 'Sends a photo of dan sheldon pointing to the specified image or text or gif, keep in mind that discord\'s gif size restrictions are a bit harsh',
        '*barrify [image]*': 'The bot uses computer vision through the OpenCV library to put barrington on identified faces in the inputed image',
        '*surprisedpikachu [image]*': 'The bot uses computer vision through the OpenCV library to put surprised pikachu on identified faces in the inputed image',
        '*marify [image]*': 'The bot uses computer vision through the OpenCV library to put marius on identified faces in the inputed image',
        '*timify [image]*': 'The bot uses computer vision through the OpenCV library to put tim on identified faces in the inputed image',
        '*calebify [image]*': 'The bot uses computer vision through the OpenCV library to put caleb on identified faces in the inputed image',
        '*$meme ["top" "bottom" image]*': 'The bot outputs the inputed image with the specified text in the old meme format',
        '*$intensify [factor image]*': 'The bot outputs the inputed image intensified to the specified factor',
        '*$highlightEdge [image]*':'The bot outputs the inputed image with an edge highlighting algorithm applied to it',
        '*$customEdgeHighlight [Red Green Blue image]*':'The bot takes in RGB values (between 0 to 255) and applies an edge highlighting algorithm where the edges are the specified color',
        '*$noise [image]*':'The bot outputs the inputed image with a noise filter applied to it',
        '*$pixelate [factor image]*':'The bot outputs the inputed image after pixelating it by a given factor, remember to use a larger factor to see results on high-res images',
        '*$mirror [axis image]*':'The bot mirrors the image on the given axis (X or Y), and outputs the result',
        '*$saturate [factor image]*':'The bot saturates the given image by the given factor',
        '*$okay* [image]':'The bot turns the given image into a video with marius saying okay as the background noise',
        '*$erase*': 'Deletes the most recent m/bdraw or barrify generated by the bot',
    }
    embed.set_author(name='Help', icon_url='https://cdn.discordapp.com/attachments/501594682820788224/558396074868342785/UMass_Stem_discord_logo.png')
    for command in ROLE_COMMANDS:
        embed.add_field(
            name = command,
            value = ROLE_COMMANDS[command]
        )
    embed.add_field(
        name = '-------------------------------------------------------------------',
        value = '------------------------------MEMES-------------------------------'
    )
    for command in MEME_COMMANDS:
        embed.add_field(
            name = command,
            value = MEME_COMMANDS[command]
        )
    await client.say(embed=embed)

@client.command(name = 'members')
async def server_members():
    num_members = len(set(client.get_all_members()))
    await client.say('There are ' + str(num_members) + ' server members')

@client.command(name='get', pass_context = True)
async def get_role(requested_role):
    """Command to get the requested role

       Args:
        - requested_role: context that the command occured use this to access the message and other attributes
    """
    member = requested_role.message.author
    if requested_role.message.server.id == '387465995176116224':
        if requested_role.message.channel.id == '537732009108439048':
            await stem_add_role(requested_role, member, client)
        else:
            await client.send_message(requested_role.message.channel, embed=discord.Embed(description="In order to decrease spam, role commands are restricted to #role-assignment", color=discord.Color.dark_red()))
    else:
        await client.send_message(requested_role.message.channel, embed=discord.Embed(description="Roles are not yet supported on this server", color=discord.Color.dark_red()))

@client.command(name='remove', pass_context = True)
async def remove_role(requested_role):
    """Command to remove the requested role

       Args:
        - requested_role: context that the command occured use this to access the message and other attributes
    """
    member = requested_role.message.author
    if requested_role.message.server.id == '387465995176116224':
        await stem_remove_role(requested_role, member, client)
    else:
        await client.send_message(requested_role.message.channel, embed=discord.Embed(description="Roles are not yet supported on this server", color=discord.Color.dark_red()))

@client.command(name='getlist', pass_context = True)
async def get_list(ctx):
    """Command to generate list of roles accessable with the get command

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await list_roles(ctx, client) # found in stem_roles.py

@client.command(name='myroles', pass_context = True)
async def my_roles(ctx):
    """Command to generate a list of the users current roles

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    member = ctx.message.author
    await list_my_roles(ctx, client, member) # found in stem_roles.py

@client.command(name='mdraw', pass_context = True)
async def mdraw(ctx):
    """Command to generate a meme of marius drawing on the image or text or gif

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    #in case of gif
    url = get_gif_url(ctx, 7)
    if url != 0:
        #get list of modified frames (has the prof drawing the image)
        imgList = gif_url_to_image_list(url, 0)
        if imgList == 0:
            #if invalid list, return
            await client.send_message(ctx.message.channel, embed=discord.Embed(description="invalid image", color=discord.Color.red()))
            return
        #get a list of imageClips for each frame
        gifClip = make_draw_gif(imgList, 1)
        gifClip.write_gif("mdraw.gif", 24, program='imageio')
        try:
            #try sending, if gif is above 8mb then an error will be thrown
            message = await client.send_file(ctx.message.channel, "mdraw.gif")
        except:
            #random color because why not
            randRGB = lambda: random.randint(0, 255)
            randColor=int('%02X%02X%02X' % (randRGB(), randRGB(), randRGB()), 16)
            os.remove("mdraw.gif")
            await client.send_message(ctx.message.channel, embed=discord.Embed(description="GIF + image becomes too large to send, sorry :(", color=randColor))
            return
        track_command(ctx.message.author.id, message)
        os.remove("mdraw.gif")
        return
    await draw_universal(ctx, 'memes/marius/draw.png', 7, marius_origin, 'marius-drawing.png')

@client.command(name='bdraw', pass_context = True)
async def bdraw(ctx):
    """Command to generate a meme of barr drawing on the image or text or gif

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    #in case of gif
    url = get_gif_url(ctx, 7)
    if url != 0:
        #get list of frames
        imgList = gif_url_to_image_list(url, 1)
        if imgList == 0:
            #if invalid list return
            await client.send_message(ctx.message.channel, embed=discord.Embed(description="invalid image", color=discord.Color.red()))
            return
            #get list of image clips
        gifClip = make_draw_gif(imgList, 0)
        gifClip.write_gif("bdraw.gif", 24, program='imageio')
        try:
            #check if message is <8 mb
            message = await client.send_file(ctx.message.channel, "bdraw.gif")
        except:
            #random color cause why not
            randRGB = lambda: random.randint(0, 255)
            randColor=int('%02X%02X%02X' % (randRGB(), randRGB(), randRGB()), 16)
            os.remove("bdraw.gif")
            await client.send_message(ctx.message.channel, embed=discord.Embed(description="GIF + image becomes too large to send, sorry :(", color=randColor))
            return
        track_command(ctx.message.author.id, message)
        os.remove("bdraw.gif")
        return
    await draw_universal(ctx, 'memes/barrington/bdraw.png', 7, barr_origin, 'barrington-drawing.png')

@client.command(name='tdraw', pass_context = True)
async def tdraw(ctx):
    """Command to generate a meme of tim drawing on the image or text or gif

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    #in case of gif
    url = get_gif_url(ctx, 7)
    if url != 0:
        #get list of frames
        imgList = gif_url_to_image_list(url, 3)
        if imgList == 0:
            await client.send_message(ctx.message.channel, embed=discord.Embed(description="invalid image", color=discord.Color.red()))
            return
        #get list of imageClips
        gifClip = make_draw_gif(imgList, 2)
        gifClip.write_gif("tdraw.gif", 24, program='imageio')
        try:
            #check for appropriate size
            message = await client.send_file(ctx.message.channel, "tdraw.gif")
        except:
            #random color cause ¯\_(ツ)_/¯
            randRGB = lambda: random.randint(0, 255)
            randColor=int('%02X%02X%02X' % (randRGB(), randRGB(), randRGB()), 16)
            os.remove("tdraw.gif")
            await client.send_message(ctx.message.channel, embed=discord.Embed(description="GIF + image becomes too large to send, sorry :(", color=randColor))
            return
        track_command(ctx.message.author.id, message)
        os.remove("tdraw.gif")
        return
    await draw_universal(ctx, 'memes/tim/tdraw.png', 7, tim_origin, 'tim-drawing.png')

@client.command(name='ldraw', pass_context = True)
async def ldraw(ctx):
    """Command to generate a meme of lan drawing on the image or text or gif

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    #in case of gif
    url = get_gif_url(ctx, 7)
    if url != 0:
        #get list of frames
        imgList = gif_url_to_image_list(url, 3)
        if imgList == 0:
            #check for valid list
            await client.send_message(ctx.message.channel, embed=discord.Embed(description="invalid image", color=discord.Color.red()))
            return
        #get list of image clips
        gifClip = make_draw_gif(imgList, 4)
        gifClip.write_gif("ldraw.gif", 24, program='imageio')
        try:
            #check for appropriate size
            message = await client.send_file(ctx.message.channel, "ldraw.gif")
        except:
            #random colors are fun, plus this doesn't need consistency
            randRGB = lambda: random.randint(0, 255)
            randColor=int('%02X%02X%02X' % (randRGB(), randRGB(), randRGB()), 16)
            os.remove("ldraw.gif")
            await client.send_message(ctx.message.channel, embed=discord.Embed(description="GIF + image becomes too large to send, sorry :(", color=randColor))
            return
        track_command(ctx.message.author.id, message)
        os.remove("ldraw.gif")
        return
    await draw_universal(ctx, 'memes/lan/lan-draw.png', 7, lan_origin, 'lan-drawing.png')

@client.command(name='landrew', pass_context = True)
async def landrew(ctx):
    """Command to generate a meme of lan drawing on the image or text

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    #in case of gif
    url = get_gif_url(ctx, 9)
    if url != 0:
        #get list of frames
        imgList = gif_url_to_image_list(url, 3)
        if imgList == 0:
            await client.send_message(ctx.message.channel, embed=discord.Embed(description="invalid image", color=discord.Color.red()))
            return
        #get list of imageClips
        gifClip = make_draw_gif(imgList, 6)
        gifClip.write_gif("landraws.gif", 24, program='imageio')
        try:
            #check whether size is appropriate
            message = await client.send_file(ctx.message.channel, "landraws.gif")
        except:
            #¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯
            randRGB = lambda: random.randint(0, 255)
            randColor=int('%02X%02X%02X' % (randRGB(), randRGB(), randRGB()), 16)
            os.remove("landraws.gif")
            await client.send_message(ctx.message.channel, embed=discord.Embed(description="GIF + image becomes too large to send, sorry :(", color=randColor))
            return
        track_command(ctx.message.author.id, message)
        os.remove("landraws.gif")
        return
    await draw_universal(ctx, 'memes/lan/landrew.png', 9, landrew_origin, 'landrew-drawing.png')

@client.command(name='shelpoint', pass_context = True)
async def shelpoint(ctx):
    """Command to generate a meme of Dan Sheldon drawing on the image or text or gif

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    #in case of gif
    url = get_gif_url(ctx, 11)
    if url != 0:
        #get list of frames
        imgList = gif_url_to_image_list(url, 3)
        if imgList == 0:
            await client.send_message(ctx.message.channel, embed=discord.Embed(description="invalid image", color=discord.Color.red()))
            return
        #get list of imageClips
        gifClip = make_draw_gif(imgList, 3)
        gifClip.write_gif("shelpoint.gif", 24, program='imageio')
        try:
            #check whether size is appropriate
            message = await client.send_file(ctx.message.channel, "shelpoint.gif")
        except:
            #¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯
            randRGB = lambda: random.randint(0, 255)
            randColor=int('%02X%02X%02X' % (randRGB(), randRGB(), randRGB()), 16)
            os.remove("shelpoint.gif")
            await client.send_message(ctx.message.channel, embed=discord.Embed(description="GIF + image becomes too large to send, sorry :(", color=randColor))
            return
        track_command(ctx.message.author.id, message)
        os.remove("shelpoint.gif")
        return
    await draw_universal(ctx, 'memes/sheldraw.png', 11, shel_origin, 'sheldon-pointing.png')

@client.command(name='handdraw', pass_context = True)
async def handdraw(ctx):
    """Command to generate a meme of a hand drawing on the image or text

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
     #in case of gif
    url = get_gif_url(ctx, 10)
    if url != 0:
        #get list of frames
        imgList = gif_url_to_image_list(url, 3)
        if imgList == 0:
            #if invalid list return
            await client.send_message(ctx.message.channel, embed=discord.Embed(description="invalid image", color=discord.Color.red()))
            return
            #get list of imageClips
        gifClip = make_draw_gif(imgList, 5)
        gifClip.write_gif("handdraw.gif", 24, program='imageio')
        try:
            #check if message is <8 mb
            message = await client.send_file(ctx.message.channel, "bdraw.gif")
        except:
            #random color cause why not
            randRGB = lambda: random.randint(0, 255)
            randColor=int('%02X%02X%02X' % (randRGB(), randRGB(), randRGB()), 16)
            os.remove("handdraw.gif")
            await client.send_message(ctx.message.channel, embed=discord.Embed(description="GIF + image becomes too large to send, sorry :(", color=randColor))
            return
        track_command(ctx.message.author.id, message)
        os.remove("handdraw.gif")
        return
    await draw_universal(ctx, 'memes/hand.png', 10, hand_origin, 'handdraw.png')

async def draw_universal(ctx, path, command_end_index, origin, name):
    """Universal function which is called by draw command with the following arguments

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
        - path: path to the drawing image (ie memes/lan/landrew.png)
        - command_end_index: index the end of the command (ie. for bdraw its 7 for '$' 'b' 'd' 'r' 'a' 'w' ' ')
        - origin: pixel origin imported from overlay.py
        - name: output file name
    """
    url = get_image_url(ctx, command_end_index)
    if url == 0: # no url, hand should write the inputed text
        output = draw_text(ctx.message.content[command_end_index:], Path(path), origin)
    else: # url inputed, hand should draw on the image
        output = overlay_image(url_to_image(url), Path(path), origin)
    output.save(name)
    try:
        message = await client.send_file(ctx.message.channel, name)
    except:
        message = await client.send_message(ctx.message.channel, embed=discord.Embed(description="Image too large", color=discord.Color.red()))
    track_command(ctx.message.author.id, message) # tracks the most recent command of a user
    os.remove(name)

#Deletes image based messages, such as bdraw, that the user requesting just sent.
@client.command(name='erase', pass_context = True)
async def erase(ctx):
    """Command to erase the most recent m/bdraw or barrify generated by the bot

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    if bot_last_command[ctx.message.author.id] is not None:
        await client.delete_message(bot_last_command[ctx.message.author.id])
        bot_last_command[ctx.message.author.id] = None #Clears this back up to avoid errors

@client.command(name='barrify', pass_context = True, aliases = ['barify'])
async def barrify(ctx, *args):
    """Command to paste barr's face on top of faces in an inputed image using facial recognition

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await ify(ctx, barr_scale, 'memes/barrington/barr-face.png', 'barrify.png', args)

@client.command(name='marify', pass_context = True, aliases=['marrify'])
async def marify(ctx, *args):
    """Command to paste marius' face on top of faces in an inputed image using facial recognition

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await ify(ctx, mar_scale, 'memes/marius/marius-face.png', 'marify.png', args)

@client.command(name='calebify', pass_context = True)
async def calebify(ctx, *args):
    """Command to paste caleb's face on top of faces in an inputed image using facial recognition

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await ify(ctx, c_scale, 'memes/caleb/caleb-face.png', 'calebify.png', args)

@client.command(name='timify', pass_context = True)
async def timify(ctx, *args):
    """Command to paste tim's face on top of faces in an inputed image using facial recognition

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await ify(ctx, tim_scale, 'memes/tim/tim-face.png', 'timify.png', args)

@client.command(name='surprisedpikachu', pass_context=True)
async def surprisedpikachu_overlay(ctx, *args):
    """Command to paste suprised pikachu on top of faces in an inputed image using facial recognition

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await ify(ctx, sp_scale, 'memes/surprised-pikachu.png', 'surprisedpikachu.png', args)

async def ify(ctx, scale, path, file_name, *args):
    """Command to paste a face on top of faces in an inputed image using facial recognition

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
        - args: arguments of the message
        - scale: specified scale for the faces
        - path: face image path
        - file_name: output file name
    """
    url = get_image_url_args(ctx, args, 1, 0)
    if url == 0: # invalid image
        await client.send_message(ctx.message.channel, embed=discord.Embed(description="Invalid image", color=discord.Color.red()))
        return
    else:
        output = paste_on_face(Path(path), url, scale)
    # if there were no faces found then send error
    if output == 0:
        await client.send_message(ctx.message.channel, embed=discord.Embed(description='No faces found, please input another image', color=discord.Color.red()))
        return

    output.save(file_name)
    message = await client.send_file(ctx.message.channel, file_name)
    track_command(ctx.message.author.id, message)
    os.remove(file_name)

@client.command(name='meme', pass_context=True)
async def meme_generator(ctx, *args):
    """Command to generate memes with top and bottom text

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
        - *args: arguments passed in with the command
    """
    url = get_image_url_args(ctx, args, 3, 2)
    if url == 0: # invalid image
        await client.send_message(ctx.message.channel, embed=discord.Embed(description="Invalid image", color=discord.Color.red()))
        return
    else:
        output = paste_text_top_bottom(args[0], args[1], url_to_image(url))
    output.save('meme.png')
    try:
        message = await client.send_file(ctx.message.channel, 'meme.png')
    except:
        message = await client.send_message(ctx.message.channel, embed=discord.Embed(description="Image too large", color=discord.Color.red()))
    track_command(ctx.message.author.id, message)
    os.remove('meme.png')

@client.command(name='intensify', pass_context = True)
async def intensify(ctx, *args):
    """Command to intensify inputed image by the inputed factor

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
        - *args: arguments passed in with the command
    """
    try:
        factor = float(args[0])
    except:
        factor = 2 # default if no factor specified
    url = get_image_url_args(ctx, args, 2, 1)
    if url == 0: # invalid image
        await client.send_message(ctx.message.channel, embed=discord.Embed(description="Invalid image", color=discord.Color.red()))
        return
    output = intensify_image(url_to_image(url), factor)
    if output == 0: # if factor < 0
        await client.send_message(ctx.message.channel, embed=discord.Embed(description="Invalid factor", color=discord.Color.red()))
        return
    # save and send image
    output.save('intensify.png')
    try:
        message = await client.send_file(ctx.message.channel, 'intensify.png')
    except:
        message = await client.send_message(ctx.message.channel, embed=discord.Embed(description="Image too large", color=discord.Color.red()))
    track_command(ctx.message.author.id, message)
    os.remove('intensify.png')

@client.command(name='mirror', pass_context = True)
async def mirror(ctx, *args):
    """Command to mirror given image on the inputted axis

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
        - *args: arguments passed in to the command (in this case either the X axis or Y axis)
    """
    try:
        url = get_image_url_args(ctx, args, 2, 2)
        axis = args[0]
    except:
        await client.send_message(ctx.message.channel, embed=discord.Embed(description="Invalid input", color=discord.Color.red()))
    if axis != "x" and axis != "y" and axis != "X" and axis != "Y":
        await client.send_message(ctx.message.channel, embed=discord.Embed(description="Invalid axis, please use x or y", color=discord.Color.red()))
        return
    if axis == "x" or axis == "X":
        output = mirror_x(url_to_image(url))
        output.save("mirror_x.png")
        try:
            message = await client.send_file(ctx.message.channel, "mirror_x.png")
        except:
            message = await client.send_message(ctx.message.channel, embed=discord.Embed(description="Image too large", color=discord.Color.red()))
        track_command(ctx.message.author.id, message)
        os.remove("mirror_x.png")
        return
    if axis == "y" or axis == "Y":
        output = mirror_y(url_to_image(url))
        output.save("mirror_y.png")
        try:
            message = await client.send_file(ctx.message.channel, "mirror_y.png")
        except:
            message = await client.send_message(ctx.message.channel, embed=discord.Embed(description="Image too large", color=discord.Color.red()))
        track_command(ctx.message.author.id, message)
        os.remove("mirror_y.png")

@client.command(name='highlightEdge', pass_context = True, aliases=['highlight', 'edge'])
async def highlight_edge(ctx, *args):
    """Command to apply an edge highlighting algorithm to a given image

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    url = get_image_url_args(ctx, args, 1, 0)
    if url == 0:
        await client.send_message(ctx.message.channel, embed=discord.Embed(description="Invalid Image"), color=discord.Color.red())
        return
    output = highlight_image(url_to_image(url))
    output.save('highlighted.png')
    try:
        message = await client.send_file(ctx.message.channel, 'highlighted.png')
    except:
        message = await client.send_message(ctx.message.channel, embed=discord.Embed(description="Image too large", color=discord.Color.red()))
    track_command(ctx.message.author.id, message)
    os.remove('highlighted.png')

@client.command(name='customEdgeHighlight', pass_context=True, aliases=['customhighlight', 'customedge'])
async def custom_edge_highlight(ctx, *args):
    """Command to highlight an image's edges and turn them into a given color

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
        - *args: arguments passed in with the command (in this case the RGB values for the edge color)
    """
    try:
        red = int(args[0])
        green = int(args[1])
        blue = int(args[2])
    except:
        await client.send_message(ctx.message.channel, embed=discord.Embed(description="Invalid Parameters", color=discord.Color.red()))
        return
    url = get_image_url_args(ctx, args, 4, 3)
    if url == 0:
        await client.send_message(ctx.message.channel, embed=discord.Embed(description="Invalid Image", color=discord.Color.red()))
        return
    output = custom_edge_highlight_image(url_to_image(url), red, green, blue)
    if output == 0: #if the RGB values are invalid
        await client.send_message(ctx.message.channel, embed=discord.Embed(description="Invalid RGB Values, please input numbers between 0-255", color=discord.Color.red()))
        return
    output.save('custom_highlight.png')
    try:
        message = await client.send_file(ctx.message.channel, 'custom_highlight.png')
    except:
        message = await client.send_message(ctx.message.channel, embed=discord.Embed(description="Image too large", color=discord.Color.red()))
    track_command(ctx.message.author.id, message)
    os.remove('custom_highlight.png')

@client.command(name='noise', pass_context=True)
async def noise_filter(ctx):
    """Command to apply a noise filter on the inputted image

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    url = get_image_url(ctx, 7)
    if url == 0:
        await client.send_message(ctx.message.channel, embed=discord.Embed(description="Invalid Image", color=discord.Color.red()))
        return
    output = scramble_pixels(url_to_image(url))
    output.save('noise.png')
    try:
        message = await client.send_file(ctx.message.channel, 'noise.png')
    except:
        message = await client.send_message(ctx.message.channel, embed=discord.Embed(description="Image too large", color=discord.Color.red()))
    track_command(ctx.message.author.id, message)
    os.remove('noise.png')

@client.command(name='pixelate', pass_context=True, aliases=['pixel'])
async def pixelate(ctx, *args):
    """Command to pixelate a given image by a given factor

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
        - *args: arguments passed into the command (in this case the pixelation factor)
    """
    url = get_image_url_args(ctx, args, 2, 1)
    try:
        factor = float(args[0])
    except:
        await client.send_message(ctx.message.channel, embed=discord.Embed(description="Invalid Parameters", color=discord.Color.red()))
        return
    if url == 0:
        await client.send_message(ctx.message.channel, embed=discord.Embed(description="Invalid Image", color=discord.Color.red()))
        return
    output = pixelate_image(url_to_image(url), factor)
    output.save('pixelate.png')
    try:
        message = await client.send_file(ctx.message.channel, 'pixelate.png')
    except:
        message = await client.send_message(ctx.message.channel, embed=discord.Embed(description="Image too large", color=discord.Color.red()))
    track_command(ctx.message.author.id, message)
    os.remove('pixelate.png')

@client.command(name='saturate', pass_context=True)
async def saturate(ctx, *args):
    """Command to saturate a given image by a given factor

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
        - *args: arguments passed into the command (in this case the pixelation factor)
    """
    url = get_image_url_args(ctx, args, 2, 1)
    try:
        factor = float(args[0])
    except:
        await client.send_message(ctx.message.channel, embed=discord.Embed(description="Invalid Parameters", color=discord.Color.red()))
        return
    if url == 0:
        await client.send_message(ctx.message.channel, embedd=discord.Embed(description="Invalid Image", color=discord.Color.red()))
        return
    output = saturate_image(url_to_image(url), factor)
    output.save('saturate.png')
    try:
        message = await client.send_file(ctx.message.channel, 'saturate.png')
    except:
        message = await client.send_message(ctx.message.channel, embed=discord.Embed(description="Image too large", color=discord.Color.red()))
    track_command(ctx.message.author.id, message)
    os.remove('saturate.png')

@client.command(name='okay', pass_context=True)
async def make_okay(ctx):
    """Command to turn a given image into a video where marius says 'okay' in the background

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    url = get_image_url(ctx, 6)
    if url == 0:
        await client.send_message(ctx.message.channel, embed=discord.Embed(description="Invalid Image", color=discord.Color.red()))
        return
    clip = make_okay_clip(url_to_image(url))
    clip.write_videofile("okay.mp4", audio="sfx/okayturnedupto8.mp3", fps=24)
    try:
        message = await client.send_file(ctx.message.channel, "okay.mp4")
    except:
        message = await client.send_message(ctx.message.channel, embed=discord.Embed(description="Image too large", color=discord.Color.red()))
    track_command(ctx.message.author.id, message)
    os.remove("okay.mp4")



def track_command(author, bot_message):
    """tracks the authors most recent command

       Args:
        - author: author of the message
        - bot_message: most recent message sent by the bot corresponding to the author
    """
    bot_last_command[author] = bot_message

client.run(BOT_TOKEN)
