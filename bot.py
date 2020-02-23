import random
import shelve
from io import BytesIO
from pathlib import Path
import discord
from discord import Game
from discord.ext.commands import Bot
import asyncio
import imageio
imageio.plugins.ffmpeg.download()
import moviepy.editor as mp
import overlay
import filters
import stem_role_commands
import face_detection
import custom_meme
import os
import time

BOT_PREFIX = "$"
BOT_TOKEN = os.environ.get('BOT_TOKEN')
BOT_ROLE = "bots"

client = Bot(command_prefix=BOT_PREFIX)
client.remove_command('help')

@client.event
async def on_ready():
    """This function runs when the bot is started"""
    game = discord.Game(name = '#rules | $help')
    await client.change_presence(activity=game)
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_member_join(member):
    if member.guild.id == 387465995176116224:
        welcome_channel = client.get_channel(387465995176116226) # introductions

        num_members = len(set(client.get_all_members()))

        # used to randomly pick one of the available drawing professors
        professor_chosen = random.randint(0, 6)

        welcome_message = 'Welcome ' + member.display_name + '!|You are member ' + str(num_members) + '!|To see all the channels set your major|and housing roles in #role-assignment!'
        if professor_chosen == 0:
            output = overlay.draw_text(welcome_message, Path('memes/barrington/bdraw.png'), overlay.barr_origin)
        elif professor_chosen == 1:
            output = overlay.draw_text(welcome_message, Path('memes/marius/draw.png'), overlay.marius_origin)
        elif professor_chosen == 2:
            output = overlay.draw_text(welcome_message, Path('memes/tim/tdraw.png'), overlay.tim_origin)
        elif professor_chosen == 3:
            output = overlay.draw_text(welcome_message, Path('memes/lan/lan-draw.png'), overlay.lan_origin)
        elif professor_chosen == 4:
            output = overlay.draw_text(welcome_message, Path('memes/lan/landrew.png'), overlay.landrew_origin)
        else:
            output = overlay.draw_text(welcome_message, Path('memes/sheldraw.png'), overlay.shel_origin)
        name = 'welcome-' + member.display_name + '.png'
        output.save(name)
        await welcome_channel.send(member.mention, file=discord.File(name))
        os.remove(name)
        embed = discord.Embed(
            color = discord.Color.blue()
        )
        embed.set_author(name='Welcome to the UMass Amherst STEM Discord Server', icon_url='https://cdn.discordapp.com/attachments/501594682820788224/558396074868342785/UMass_Stem_discord_logo.png')
        embed.add_field(
                name = 'How to see all the channels',
                value = 'Set at least one housing role and at least one major role\nTo set roles go to **#role-assignment** and use the `$get` command\n\nFor example, if you live off campus and you\'re a chemistry major you would run these two commands:\n\n`$get Off-Campus`\n`$get Chemistry`\n\n*If you would like to see all the possible housing and major roles run the `$getlist` command*\n\n*If you have graduated already you may use the `Almuni` role in place of a housing role, if you are considering or planning on attending UMass and don\'t yet have a residential area you should assign yourself the `Prospective Student` role*',
                inline = False
            )
        await member.send(embed=embed)
    
@client.event
async def on_message(message):
    author = message.author
    try:
        if message.guild.id == 387465995176116224:
            data = shelve.open('server-data/stem-discord-data')
            if (BOT_ROLE not in [role.name.lower() for role in author.roles]):
                if str(author) in data:
                    data[str(author)] += 1
                else:
                    data[str(author)] = 1
            data['Total Messages'] += 1
            data.close()
    except:
        pass
    await client.process_commands(message)

    


@client.event
async def on_message_delete(message):
    """This function runs whenever a message is deleted

       Args:
        - message: context of the deleted message (used to get the message contents)
    """
    author = message.author
    channel = client.get_channel(557002016782680076)
    try:
        if message.guild.id == 387465995176116224:
            if (BOT_ROLE not in [role.name.lower() for role in author.roles]) and author.id != '98138045173227520':
                content = message.content
                await channel.send('_Deleted Message_\n**Message sent by:** ' + author.mention + '\n**Channel:** ' + message.channel.mention + '\n**Contents:** *' + content + '*\n--------------')
    except:
        pass
@client.event
async def on_message_edit(before, after):
    """This function runs whenever a message is edited

       Args:
        - before: context before the edit (use to get the message contents before the message was edited)
        - after: context after the edit (use to get the message contents after the message was edited)
    """
    author = before.author
    channel = client.get_channel(557002016782680076)
    try:
        if before.guild.id == 387465995176116224: # UMass STEM Discord server ID
            if (BOT_ROLE not in [role.name.lower() for role in author.roles]) and author.id != '98138045173227520':
                before_content = before.content
                after_content = after.content
                await channel.send('_Edited Message_\n**Message sent by:** ' + author.mention + '\n**Channel:** ' + before.channel.mention + '\n**Pre-edit contents:** *' + before_content + '*\n**Post-edit contents:** *'+ after_content + '*\n--------------')
    except:
        pass
@client.command(name='help')
async def help(ctx):
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
    embed.add_field(
        name = '-------------------------------------------------------------------',
        value = '------------------------------ROLES------------------------------',
        inline = False
    )
    
    for command in ROLE_COMMANDS:
        embed.add_field(
            name = command,
            value = ROLE_COMMANDS[command],
            inline = False
        )
    embed.add_field(
        name = '-------------------------------------------------------------------',
        value = '------------------------------MEMES------------------------------',
        inline = False
    )
    for command in MEME_COMMANDS:
        embed.add_field(
            name = command,
            value = MEME_COMMANDS[command],
            inline = False
        )
    await ctx.send(embed=embed)

@client.command(name = 'leaderboard')
async def display_leaderboard(ctx):
    data = shelve.open('server-data/stem-discord-data')
    data_dict = dict(data)
    number = 0
    top_10 = ''
    # sort dictionary and only take top ten
    for user in sorted(data, key=data.get, reverse=True):
        if number == 0:
            number+= 1
            continue
        elif number < 11:
            top_10 += '**' + str(number) + '**. ' + user + ' - ' + str(data[user]) + '\n'
        else:
            break
        number += 1
    top_10 += '*Total Messages*: ' + str(data['Total Messages'])
    data.close()
    await ctx.send(embed=discord.Embed(title='Server Message Leaderboard', description=top_10, color=discord.Color.purple()))

@client.command(name = 'refresh_leaderboard')
async def refresh_count_messages(ctx):
    if ctx.author.id == 98138045173227520: # only caleb can use this command
        async with ctx.channel.typing():
            os.remove('server-data/stem-discord-data.dir')
            os.remove('server-data/stem-discord-data.bak')
            os.remove('server-data/stem-discord-data.dat')
            data = shelve.open('server-data/stem-discord-data')
            data['Total Messages'] = 0
            # build dictionary of user: # of messages
            for channel in ctx.guild.text_channels:
                print(channel.name)
                async for message in channel.history(limit=100000):
                    try:
                        if (BOT_ROLE not in [role.name.lower() for role in message.author.roles]):
                            if str(message.author) in data:
                                data[str(message.author)] += 1
                            else:
                                data[str(message.author)] = 1
                    except:
                        pass
                    data['Total Messages'] += 1
            data.close()
            
            await ctx.send(embed=discord.Embed(description='Leaderboard refresh complete', color=discord.Color.green()))

@client.command(name = 'members')
async def server_members(ctx):
    num_members = len(set(client.get_all_members()))
    await ctx.send('There are ' + str(num_members) + ' server members')

@client.command(name='get')
async def get_role(requested_role):
    """Command to get the requested role

       Args:
        - requested_role: context that the command occured use this to access the message and other attributes
    """
    member = requested_role.author
    channel = requested_role.channel
    if requested_role.guild.id == 387465995176116224:
        if requested_role.channel.id == 537732009108439048 or requested_role.channel.id == 501594682820788224:
            await stem_role_commands.stem_add_role(requested_role, member, client)
        else:
            await channel.send(embed=discord.Embed(description="In order to decrease spam, role commands are restricted to #role-assignment", color=discord.Color.dark_red()))
    else:
        await channel.send(embed=discord.Embed(description="Roles are not yet supported on this server", color=discord.Color.dark_red()))

@client.command(name='remove')
async def remove_role(requested_role):
    """Command to remove the requested role

       Args:
        - requested_role: context that the command occured use this to access the message and other attributes
    """
    member = requested_role.author
    channel = requested_role.channel
    if requested_role.guild.id == 387465995176116224:
        if requested_role.channel.id == 537732009108439048 or requested_role.channel.id == 501594682820788224:
            await stem_role_commands.stem_remove_role(requested_role, member, client)
        else:
            await channel.send(embed=discord.Embed(description="In order to decrease spam, role commands are restricted to #role-assignment", color=discord.Color.dark_red()))
    else:
        await channel.send(embed=discord.Embed(description="Roles are not yet supported on this server", color=discord.Color.dark_red()))

@client.command(name='getlist')
async def get_list(ctx):
    """Command to generate list of roles accessable with the get command

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await stem_role_commands.list_roles(ctx, client)

@client.command(name='myroles')
async def my_roles(ctx):
    """Command to generate a list of the users current roles

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    mentions = ctx.message.mentions
    channel = ctx.channel
    if len(mentions) < 1:
        member = ctx.author
    elif len(mentions) == 1:
        member = mentions[0]
    else:
        await channel.send(embed=discord.Embed(description="Too many users specified, please mention less than two users", color=discord.Color.red()))
        return
    await stem_role_commands.list_my_roles(ctx, client, member) # found in stem_role_commands.py

@client.command(name='mdraw')
async def mdraw(ctx):
    """Command to generate a meme of marius drawing on the image or text or gif

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await custom_meme.draw_universal(ctx, 'memes/marius/draw.png', 7, overlay.marius_origin, 'marius-drawing')

@client.command(name='bdraw')
async def bdraw(ctx):
    """Command to generate a meme of barr drawing on the image or text or gif

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await custom_meme.draw_universal(ctx, 'memes/barrington/bdraw.png', 7, overlay.barr_origin, 'barrington-drawing')

@client.command(name='tdraw')
async def tdraw(ctx):
    """Command to generate a meme of tim drawing on the image or text or gif

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await custom_meme.draw_universal(ctx, 'memes/tim/tdraw.png', 7, overlay.tim_origin, 'tim-drawing')

@client.command(name='ldraw')
async def ldraw(ctx):
    """Command to generate a meme of lan drawing on the image or text or gif

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await custom_meme.draw_universal(ctx, 'memes/lan/lan-draw.png', 7, overlay.lan_origin, 'lan-drawing')

@client.command(name='landrew')
async def landrew(ctx):
    """Command to generate a meme of lan drawing on the image or text

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await custom_meme.draw_universal(ctx, 'memes/lan/landrew.png', 9, overlay.landrew_origin, 'landrew-drawing')

@client.command(name='shelpoint')
async def shelpoint(ctx):
    """Command to generate a meme of Dan Sheldon drawing on the image or text or gif

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await custom_meme.draw_universal(ctx, 'memes/sheldraw.png', 11, overlay.shel_origin, 'sheldon-pointing')

@client.command(name='handdraw')
async def handdraw(ctx):
    """Command to generate a meme of a hand drawing on the image or text

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await custom_meme.draw_universal(ctx, 'memes/hand.png', 10, overlay.hand_origin, 'handdraw')

@client.command(name='erase')
async def erase(ctx):
    """Command to erase the most recent m/bdraw or barrify generated by the bot

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    if custom_meme.bot_last_command[ctx.author.id] is not None:
        await client.delete_message(custom_meme.bot_last_command[ctx.author.id])
        custom_meme.bot_last_command[ctx.author.id] = None #Clears this back up to avoid errors

@client.command(name='barrify', aliases = ['barify'])
async def barrify(ctx, *args):
    """Command to paste barr's face on top of faces in an inputed image using facial recognition

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await custom_meme.ify(ctx, face_detection.barr_scale, 'memes/barrington/barr-face.png', 'barrify.png', args)

@client.command(name='marify', aliases=['marrify'])
async def marify(ctx, *args):
    """Command to paste marius' face on top of faces in an inputed image using facial recognition

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await custom_meme.ify(ctx, face_detection.mar_scale, 'memes/marius/marius-face.png', 'marify.png', args)

@client.command(name='timify')
async def timify(ctx, *args):
    """Command to paste tim's face on top of faces in an inputed image using facial recognition

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await custom_meme.ify(ctx, face_detection.tim_scale, 'memes/tim/tim-face.png', 'timify.png', args)

@client.command(name='surprisedpikachu', pass_context=True)
async def surprisedpikachu_overlay(ctx, *args):
    """Command to paste suprised pikachu on top of faces in an inputed image using facial recognition

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await custom_meme.ify(ctx, face_detection.sp_scale, 'memes/surprised-pikachu.png', 'surprisedpikachu.png', args)

@client.command(name='meme', pass_context=True)
async def meme_generator(ctx, *args):
    """Command to generate memes with top and bottom text

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
        - *args: arguments passed in with the command
    """
    channel = ctx.channel
    url = overlay.get_image_url_args(ctx, args, 3, 2)
    if url == 0: # invalid image
        await channel.send(embed=discord.Embed(description="Invalid image", color=discord.Color.red()))
        return
    else:
        output = overlay.paste_text_top_bottom(args[0], args[1], overlay.url_to_image(url))
    output.save('meme.png')
    try:
        message = await channel.send(file=discord.File('meme.png'))
    except:
        message = await channel.send(embed=discord.Embed(description="Image too large", color=discord.Color.red()))
    custom_meme.track_command(ctx.author.id, message)
    os.remove('meme.png')

@client.command(name='intensify')
async def intensify(ctx, *args):
    """Command to intensify inputed image by the inputed factor

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
        - *args: arguments passed in with the command
    """
    channel = ctx.channel
    try:
        factor = float(args[0])
        url = overlay.get_image_url_args(ctx, args, 2, 1)
    except:
        factor = 2 # default if no factor specified
        url = overlay.get_image_url_args(ctx, args, 1, 0)    
    if url == 0: # invalid image
        await channel.send(embed=discord.Embed(description="Invalid image", color=discord.Color.red()))
        return
    output = filters.intensify_image(overlay.url_to_image(url), factor)
    if output == 0: # if factor < 0
        await channel.send(embed=discord.Embed(description="Invalid factor", color=discord.Color.red()))
        return
    # save and send image
    output.save('intensify.png')
    try:
        message = await channel.send(file=discord.File('intensify.png'))
    except:
        message = await channel.send(embed=discord.Embed(description="Image too large", color=discord.Color.red()))
    custom_meme.track_command(ctx.author.id, message)
    os.remove('intensify.png')

@client.command(name='mirror')
async def mirror(ctx, *args):
    """Command to mirror given image on the inputted axis

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
        - *args: arguments passed in to the command (in this case either the X axis or Y axis)
    """
    channel = ctx.channel
    try:
        url = overlay.get_image_url_args(ctx, args, 2, 2)
        axis = args[0]
    except:
        await channel.send(embed=discord.Embed(description="Invalid input", color=discord.Color.red()))
    if axis != "x" and axis != "y" and axis != "X" and axis != "Y":
        await channel.send(embed=discord.Embed(description="Invalid axis, please use x or y", color=discord.Color.red()))
        return
    if axis == "x" or axis == "X":
        output = filters.mirror_x(overlay.url_to_image(url))
        output.save("mirror_x.png")
        try:
            message = await channel.send(file=discord.File("mirror_x.png"))
        except:
            message = await channel.send(embed=discord.Embed(description="Image too large", color=discord.Color.red()))
        custom_meme.track_command(ctx.author.id, message)
        os.remove("mirror_x.png")
        return
    if axis == "y" or axis == "Y":
        output = filters.mirror_y(overlay.url_to_image(url))
        output.save("mirror_y.png")
        try:
            message = await channel.send(file=discord.File("mirror_y.png"))
        except:
            message = await channel.send(embed=discord.Embed(description="Image too large", color=discord.Color.red()))
        custom_meme.track_command(ctx.author.id, message)
        os.remove("mirror_y.png")

@client.command(name='highlightEdge', aliases=['highlight', 'edge'])
async def highlight_edge(ctx, *args):
    """Command to apply an edge highlighting algorithm to a given image

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    channel = ctx.channel
    url = overlay.get_image_url_args(ctx, args, 1, 0)
    if url == 0:
        await channel.send(embed=discord.Embed(description="Invalid Image"), color=discord.Color.red())
        return
    output = filters.highlight_image(overlay.url_to_image(url))
    output.save('highlighted.png')
    try:
        message = await channel.send(file=discord.File('highlighted.png'))
    except:
        message = await channel.send(embed=discord.Embed(description="Image too large", color=discord.Color.red()))
    custom_meme.track_command(ctx.author.id, message)
    os.remove('highlighted.png')

@client.command(name='customEdgeHighlight', pass_context=True, aliases=['customhighlight', 'customedge'])
async def custom_edge_highlight(ctx, *args):
    """Command to highlight an image's edges and turn them into a given color

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
        - *args: arguments passed in with the command (in this case the RGB values for the edge color)
    """
    channel = ctx.channel
    try:
        red = int(args[0])
        green = int(args[1])
        blue = int(args[2])
    except:
        await channel.send(embed=discord.Embed(description="Invalid Parameters", color=discord.Color.red()))
        return
    url = overlay.get_image_url_args(ctx, args, 4, 3)
    if url == 0:
        await channel.send(embed=discord.Embed(description="Invalid Image", color=discord.Color.red()))
        return
    output = filters.custom_edge_highlight_image(overlay.url_to_image(url), red, green, blue)
    if output == 0: #if the RGB values are invalid
        await channel.send(embed=discord.Embed(description="Invalid RGB Values, please input numbers between 0-255", color=discord.Color.red()))
        return
    output.save('custom_highlight.png')
    try:
        message = await channel.send(file=discord.File('custom_highlight.png'))
    except:
        message = await channel.send(embed=discord.Embed(description="Image too large", color=discord.Color.red()))
    custom_meme.track_command(ctx.author.id, message)
    os.remove('custom_highlight.png')

@client.command(name='noise', pass_context=True)
async def noise_filter(ctx):
    """Command to apply a noise filter on the inputted image

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    channel = ctx.channel
    url = overlay.get_image_url(ctx, 7)
    if url == 0:
        await channel.send(embed=discord.Embed(description="Invalid Image", color=discord.Color.red()))
        return
    output = filters.scramble_pixels(overlay.url_to_image(url))
    output.save('noise.png')
    try:
        message = await channel.send(file=discord.File('noise.png'))
    except:
        message = await channel.send(embed=discord.Embed(description="Image too large", color=discord.Color.red()))
    custom_meme.track_command(ctx.author.id, message)
    os.remove('noise.png')

@client.command(name='pixelate', pass_context=True, aliases=['pixel'])
async def pixelate(ctx, *args):
    """Command to pixelate a given image by a given factor

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
        - *args: arguments passed into the command (in this case the pixelation factor)
    """
    channel = ctx.channel
    url = overlay.get_image_url_args(ctx, args, 2, 1)
    try:
        factor = float(args[0])
    except:
        await channel.send(embed=discord.Embed(description="Invalid Parameters", color=discord.Color.red()))
        return
    if url == 0:
        await channel.send(embed=discord.Embed(description="Invalid Image", color=discord.Color.red()))
        return
    output = filters.pixelate_image(overlay.url_to_image(url), factor)
    output.save('pixelate.png')
    try:
        message = await channel.send(file=discord.File('pixelate.png'))
    except:
        message = await channel.send(embed=discord.Embed(description="Image too large", color=discord.Color.red()))
    custom_meme.track_command(ctx.author.id, message)
    os.remove('pixelate.png')

@client.command(name='saturate', pass_context=True)
async def saturate(ctx, *args):
    """Command to saturate a given image by a given factor

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
        - *args: arguments passed into the command (in this case the pixelation factor)
    """
    channel = ctx.channel
    url = overlay.get_image_url_args(ctx, args, 2, 1)
    try:
        factor = float(args[0])
    except:
        await channel.send(embed=discord.Embed(description="Invalid Parameters", color=discord.Color.red()))
        return
    if url == 0:
        await channel.send(embedd=discord.Embed(description="Invalid Image", color=discord.Color.red()))
        return
    output = filters.saturate_image(overlay.url_to_image(url), factor)
    output.save('saturate.png')
    try:
        message = await channel.send(file=discord.File('saturate.png'))
    except:
        message = await channel.send(embed=discord.Embed(description="Image too large", color=discord.Color.red()))
    custom_meme.track_command(ctx.author.id, message)
    os.remove('saturate.png')

@client.command(name='okay', pass_context=True)
async def make_okay(ctx):
    """Command to turn a given image into a video where marius says 'okay' in the background

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    channel = ctx.channel
    url = overlay.get_image_url(ctx, 6)
    if url == 0:
        await channel.send(embed=discord.Embed(description="Invalid Image", color=discord.Color.red()))
        return
    clip = filters.make_okay_clip(overlay.url_to_image(url))
    clip.write_videofile("okay.mp4", audio="sfx/okayturnedupto8.mp3", fps=24)
    try:
        message = await channel.send(file=discord.File("okay.mp4"))
    except:
        message = await channel.send(embed=discord.Embed(description="Image too large", color=discord.Color.red()))
    custom_meme.track_command(ctx.author.id, message)
    os.remove("okay.mp4")





client.run(BOT_TOKEN)
