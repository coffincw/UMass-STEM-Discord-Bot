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
from overlay import overlay_image, url_to_image, get_image_url, get_image_url_args, draw_text, paste_text_top_bottom, marius_origin, barr_origin, tim_origin, lan_origin, landrew_origin, shel_origin, intensify_image, highlight_image, custom_edge_highlight_image, mirror_x, mirror_y, scramble_pixels, pixelate_image, saturate_image, make_okay_clip
from stem_roles import stem_add_role, stem_remove_role, list_roles
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
        professor_chosen = random.randint(0, 5)

        welcome_message = 'Welcome ' + member.display_name + '!|You are member ' + str(num_members) + '!|To see all the channels set your major|and housing roles in #role-assignment!'
        if professor_chosen == 0:
            output = draw_text(welcome_message, Path('memes/barrington/bdraw.png'), barr_origin)
        elif professor_chosen == 1:
            output = draw_text(welcome_message, Path('memes/marius/draw.png'), marius_origin)
        elif professor_chosen == 2:
            output = draw_text(welcome_message, Path('memes/tim/tdraw.png'), tim_origin)
        elif professor_chosen == 3:
            output = draw_text(welcome_message, Path('memes/lan/lan-draw.png'), lan_origin)
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
        '*$mdraw [image/url/text]*': 'Sends a photo of marius drawing the specified image or text',
        '*$tdraw [image/url/text]*': 'Sends a photo of tim drawing the specified image or text',
        '*$bdraw [image/url/text]*': 'Sends a photo of barrington drawing the specified image or text',
        '*$ldraw [image/url/text]*': 'Sends a photo of lan drawing the specified image or text',
        '*$landrew [image/url/text]*': 'Sends a photo of a different occasion of lan drawing the specified image or text',
        '*$shelpoint [image/url/text]*': 'Sends a photo of dan sheldon pointing to the specified image or text',
        '*$barrify [image]*': 'The bot uses computer vision through the OpenCV library to put barrington on identified faces in the inputed image',
        '*$surprisedpikachu [image]*': 'The bot uses computer vision through the OpenCV library to put surprised pikachu on identified faces in the inputed image',
        '*$marify [image]*': 'The bot uses computer vision through the OpenCV library to put marius on identified faces in the inputed image',
        '*$timify [image]*': 'The bot uses computer vision through the OpenCV library to put tim on identified faces in the inputed image',
        '*$calebify [image]*': 'The bot uses computer vision through the OpenCV library to put caleb on identified faces in the inputed image',
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
        value = '------------------------------MEMES--------------------------'
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
        await stem_add_role(requested_role, member, client)
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

@client.command(name='mdraw', pass_context = True)
async def mdraw(ctx):
    """Command to generate a meme of marius drawing on the image or text

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    url = get_image_url(ctx, 7)
    if url == 0:
        output = draw_text(ctx.message.content[7:], Path('memes/marius/draw.png'), marius_origin)
    else:
        output = overlay_image(url_to_image(url), Path('memes/marius/draw.png'), marius_origin)
    name = 'marius-drawing.png'
    output.save(name)
    message = await client.send_file(ctx.message.channel, name)
    track_command(ctx.message.author.id, message)
    os.remove(name)

@client.command(name='bdraw', pass_context = True)
async def bdraw(ctx):
    """Command to generate a meme of barr drawing on the image or text

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    url = get_image_url(ctx, 7)
    if url == 0: # no url, barr should write the inputed text
        output = draw_text(ctx.message.content[7:], Path('memes/barrington/bdraw.png'), barr_origin)
    else: # url inputed, barr should draw on the image
        output = overlay_image(url_to_image(url), Path('memes/barrington/bdraw.png'), barr_origin)
    output.save('barrington-drawing.png')
    message = await client.send_file(ctx.message.channel, 'barrington-drawing.png')
    track_command(ctx.message.author.id, message) # tracks the most recent command of a user
    os.remove('barrington-drawing.png')

@client.command(name='tdraw', pass_context = True)
async def tdraw(ctx):
    """Command to generate a meme of tim drawing on the image or text

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    url = get_image_url(ctx, 7)
    if url == 0: # no url, tim should write the inputed text
        output = draw_text(ctx.message.content[7:], Path('memes/tim/tdraw.png'), tim_origin)
    else: # url inputed, tim should draw on the image
        output = overlay_image(url_to_image(url), Path('memes/tim/tdraw.png'), tim_origin)
    output.save('tim-drawing.png')
    message = await client.send_file(ctx.message.channel, 'tim-drawing.png')
    track_command(ctx.message.author.id, message) # tracks the most recent command of a user
    os.remove('tim-drawing.png')

@client.command(name='ldraw', pass_context = True)
async def ldraw(ctx):
    """Command to generate a meme of lan drawing on the image or text

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    url = get_image_url(ctx, 7)
    if url == 0: # no url, lan should write the inputed text
        output = draw_text(ctx.message.content[7:], Path('memes/lan/lan-draw.png'), lan_origin)
    else: # url inputed, lan should draw on the image
        output = overlay_image(url_to_image(url), Path('memes/lan/lan-draw.png'), lan_origin)
    output.save('lan-drawing.png')
    message = await client.send_file(ctx.message.channel, 'lan-drawing.png')
    track_command(ctx.message.author.id, message) # tracks the most recent command of a user
    os.remove('lan-drawing.png')

@client.command(name='landrew', pass_context = True)
async def landrew(ctx):
    """Command to generate a meme of lan drawing on the image or text

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    url = get_image_url(ctx, 9)
    if url == 0: # no url, lan should write the inputed text
        output = draw_text(ctx.message.content[9:], Path('memes/lan/landrew.png'), landrew_origin)
    else: # url inputed, lan should draw on the image
        output = overlay_image(url_to_image(url), Path('memes/lan/landrew.png'), landrew_origin)
    output.save('landrew-drawing.png')
    message = await client.send_file(ctx.message.channel, 'landrew-drawing.png')
    track_command(ctx.message.author.id, message) # tracks the most recent command of a user
    os.remove('landrew-drawing.png')

@client.command(name='shelpoint', pass_context = True)
async def shelpoint(ctx):
    """Command to generate a meme of Dan Sheldon drawing on the image or text

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    url = get_image_url(ctx, 11)
    if url == 0: # no url, shel should write the inputed text
        output = draw_text(ctx.message.content[11:], Path('memes/sheldraw.png'), shel_origin)
    else: # url inputed, shel should draw on the image
        output = overlay_image(url_to_image(url), Path('memes/sheldraw.png'), shel_origin)
    output.save('sheldon-pointing.png')
    message = await client.send_file(ctx.message.channel, 'sheldon-pointing.png')
    track_command(ctx.message.author.id, message) # tracks the most recent command of a user
    os.remove('sheldon-pointing.png')

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
    url = get_image_url_args(ctx, args, 1, 0)
    if url == 0: # invalid image
        await client.send_message(ctx.message.channel, embed=discord.Embed(description="Invalid image", color=discord.Color.red()))
        return
    else:
        output = paste_on_face(Path('memes/barrington/barr-face.png'), url, barr_scale)
    # if there were no faces found then send error
    if output == 0:
        await client.send_message(ctx.message.channel, embed=discord.Embed(description='No faces found, please input another image', color=discord.Color.red()))
        return

    output.save('barrify.png')
    message = await client.send_file(ctx.message.channel, 'barrify.png')
    track_command(ctx.message.author.id, message)
    os.remove('barrify.png')

@client.command(name='marify', pass_context = True, aliases=['marrify'])
async def marify(ctx, *args):
    """Command to paste marius' face on top of faces in an inputed image using facial recognition

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    url = get_image_url_args(ctx, args, 1, 0)
    if url == 0: # invalid image
        await client.send_message(ctx.message.channel, embed=discord.Embed(description="Invalid image", color=discord.Color.red()))
        return
    else:
        output = paste_on_face(Path('memes/marius/marius-face.png'), url, mar_scale)
    # if there were no faces found then send error
    if output == 0:
        await client.send_message(ctx.message.channel, embed=discord.Embed(description='No faces found, please input another image', color=discord.Color.red()))
        return

    output.save('marify.png')
    message = await client.send_file(ctx.message.channel, 'marify.png')
    track_command(ctx.message.author.id, message)
    os.remove('marify.png')

@client.command(name='calebify', pass_context = True)
async def calebify(ctx, *args):
    """Command to paste caleb's face on top of faces in an inputed image using facial recognition

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    url = get_image_url_args(ctx, args, 1, 0)
    if url == 0: # invalid image
        await client.send_message(ctx.message.channel, embed=discord.Embed(description="Invalid image", color=discord.Color.red()))
        return
    else:
        output = paste_on_face(Path('memes/caleb/caleb-face.png'), url, mar_scale)
    # if there were no faces found then send error
    if output == 0:
        await client.send_message(ctx.message.channel, embed=discord.Embed(description='No faces found, please input another image', color=discord.Color.red()))
        return

    output.save('calebify.png')
    message = await client.send_file(ctx.message.channel, 'calebify.png')
    track_command(ctx.message.author.id, message)
    os.remove('calebify.png')

@client.command(name='timify', pass_context = True)
async def timify(ctx, *args):
    """Command to paste marius' face on top of faces in an inputed image using facial recognition

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    url = get_image_url_args(ctx, args, 1, 0)
    if url == 0: # invalid image
        await client.send_message(ctx.message.channel, embed=discord.Embed(description="Invalid image", color=discord.Color.red()))
        return
    else:
        output = paste_on_face(Path('memes/tim/tim-face.png'), url, tim_scale)
    # if there were no faces found then send error
    if output == 0:
        await client.send_message(ctx.message.channel, embed=discord.Embed(description='No faces found, please input another image', color=discord.Color.red()))
        return

    output.save('timify.png')
    message = await client.send_file(ctx.message.channel, 'timify.png')
    track_command(ctx.message.author.id, message)
    os.remove('timify.png')

@client.command(name='surprisedpikachu', pass_context=True)
async def surprisedpikachu_overlay(ctx):
    """Command to paste suprised pikachu on top of faces in an inputed image using facial recognition

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    url = get_image_url(ctx, 18)
    if url == 0: # invalid image
        await client.send_message(ctx.message.channel, embed=discord.Embed(description="Invalid image", color=discord.Color.red()))
        return
    else:
        output = paste_on_face(Path('memes/surprised-pikachu.png'), url, sp_scale)
    # if there were no faces found then send error
    if output == 0:
        await client.send_message(ctx.message.channel, embed=discord.Embed(description='No faces found, please input another image', color=discord.Color.red()))
        return

    output.save('surprisedpikachu.png')
    message = await client.send_file(ctx.message.channel, 'surprisedpikachu.png')
    track_command(ctx.message.author.id, message)
    os.remove('surprisedpikachu.png')

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
    message = await client.send_file(ctx.message.channel, 'meme.png')
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
    message = await client.send_file(ctx.message.channel, 'intensify.png')
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
        message = await client.send_file(ctx.message.channel, "mirror_x.png")
        track_command(ctx.message.author.id, message)
        os.remove("mirror_x.png")
        return
    if axis == "y" or axis == "Y":
        output = mirror_y(url_to_image(url))
        output.save("mirror_y.png")
        message = await client.send_file(ctx.message.channel, "mirror_y.png")
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
    message = await client.send_file(ctx.message.channel, 'highlighted.png')
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
    message = await client.send_file(ctx.message.channel, 'custom_highlight.png')
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
    message = await client.send_file(ctx.message.channel, 'noise.png')
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
    message = await client.send_file(ctx.message.channel, 'pixelate.png')
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
    message = await client.send_file(ctx.message.channel, 'saturate.png')
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
    message = await client.send_file(ctx.message.channel, "okay.mp4")
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
