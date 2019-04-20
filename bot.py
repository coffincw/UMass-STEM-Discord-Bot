import random
from io import BytesIO
from pathlib import Path
import discord
from discord import Game
from discord.ext.commands import Bot
import asyncio
from overlay import overlay_image, url_to_image, get_image_url, get_image_url_args, draw_text, paste_text_top_bottom, marius_origin, barr_origin, tim_origin, lan_origin, shel_origin, intensify_image, highlight_image, custom_edge_highlight_image
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
    await client.change_presence(game = Game(name = '#rules | $help'))
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
        professor_chosen = random.randint(0, 3)

        welcome_message = 'Welcome ' + member.display_name + '!|You are member ' + str(num_members) + '!|To see all the channels set your major|and housing roles in #role-assignment!'
        if professor_chosen == 0:
            output = draw_text(welcome_message, Path('memes/barrington/bdraw.png'), barr_origin)
        elif professor_chosen == 1:
            output = draw_text(welcome_message, Path('memes/marius/mdraw.png'), marius_origin)
        else:
            output = draw_text(welcome_message, Path('memes/tim/tdraw.png'), tim_origin)
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

@client.command()
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
        '*$shelpoint [image/url/text]*': 'Sends a photo of dan sheldon pointing to the specified image or text',
        '*barrify [image]*': 'The bot uses computer vision through the OpenCV library to put barrington on identified faces in the inputed image',
        '*surprisedpikachu [image]*': 'The bot uses computer vision through the OpenCV library to put surprised pikachu on identified faces in the inputed image',
        '*marify [image]*': 'The bot uses computer vision through the OpenCV library to put marius on identified faces in the inputed image',
        '*timify [image]*': 'The bot uses computer vision through the OpenCV library to put tim on identified faces in the inputed image',
        '*calebify [image]*': 'The bot uses computer vision through the OpenCV library to put caleb on identified faces in the inputed image',
        '*$meme ["top" "bottom" image]*': 'The bot outputs the inputed image with the specified text in the old meme format',
        '*$intensify [factor image]*': 'The bot outputs the inputed image intensified to the specified factor',
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

@client.command(name='barrify', pass_context = True)
async def barrify(ctx):
    """Command to paste barr's face on top of faces in an inputed image using facial recognition

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    url = get_image_url(ctx, 9)
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

@client.command(name='marify', pass_context = True)
async def marify(ctx):
    """Command to paste marius' face on top of faces in an inputed image using facial recognition

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    url = get_image_url(ctx, 8)
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
async def calebify(ctx):
    """Command to paste caleb's face on top of faces in an inputed image using facial recognition

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    url = get_image_url(ctx, 8)
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
async def timify(ctx):
    """Command to paste marius' face on top of faces in an inputed image using facial recognition

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    url = get_image_url(ctx, 8)
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

@client.command(name='highlightEdge', pass_context = True)
async def highlight_edge(ctx):
    url = get_image_url(ctx, 15)
    if url == 0:
        await client.send_message(ctx.message.channel, embed=discord.Embed(description="Invalid Image"), color=discord.Color.red())
        return
    output = highlight_image(url_to_image(url))
    output.save('highlighted.png')
    message = await client.send_file(ctx.message.channel, 'highlighted.png')
    track_command(ctx.message.author.id, message)
    os.remove('highlighted.png')

@client.command(name='customEdgeHighlight', pass_context=True)
async def custom_edge_highlight(ctx, *args):
    try:
        red = float(args[0])
        green = float(args[1])
        blue = float(args[2])
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

def track_command(author, bot_message):
    """tracks the authors most recent command

       Args:
        - author: author of the message
        - bot_message: most recent message sent by the bot corresponding to the author
    """
    bot_last_command[author] = bot_message

client.run(BOT_TOKEN)
