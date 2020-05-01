import random
import shelve
from io import BytesIO
from pathlib import Path
import discord
import requests
from discord import Game
from discord.ext.commands import Bot
import asyncio
import imageio
imageio.plugins.ffmpeg.download() # needed for Heroku build
import moviepy.editor as mp
import overlay
import filters
import stem_role_commands
import face_detection
import custom_meme
import coronavirus as corona
import os
import time

BOT_PREFIX = "$"
BOT_TOKEN = os.environ.get('BOT_TOKEN')
BOT_ROLE = "bots"

client = Bot(command_prefix=BOT_PREFIX, case_insensitive=True)
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
        welcome_channel = client.get_channel(705670780704391259) # introductions

        num_members = member.guild.member_count

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
        if message.guild.id == 387465995176116224 and author.id != 98138045173227520: # UMass STEM Discord server ID and not caleb
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
        if before.guild.id == 387465995176116224 and author.id != 98138045173227520: # UMass STEM Discord server ID and not caleb
            if (BOT_ROLE not in [role.name.lower() for role in author.roles]) and author.id != '98138045173227520':
                before_content = before.content
                after_content = after.content
                await channel.send('_Edited Message_\n**Message sent by:** ' + author.mention + '\n**Channel:** ' + before.channel.mention + '\n**Pre-edit contents:** *' + before_content + '*\n**Post-edit contents:** *'+ after_content + '*\n--------------')
    except:
        pass

# vvv GENERAL COMMANDS vvv

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
        '*$myroles [optional: @mention]*': 'Displays the roles of the specified user, if none given displays caller\'s roles',
        '*$stats [role]*': 'Outputs the member count and percentage of total server members for the specified role. Please do not mention the role in the command, just state the name'
    }
    GENERAL_COMMANDS = {
        '*$members*': 'Displays the number of members on the server',
        '*$leaderboard*': 'Displays the top 10 most active users on the server measured by quantity of messages',
        '*$covid* [optional: state]': 'Displays the number of cases and deaths related to COVID19 in the specified state, if no state given displays the top 15 states by cases in the U.S',
        '*covidp*': 'Displays the number of cases, and deaths related to COVID19 in the top 15 U.S states. Sorted by percentage of the state infected.'
    }
    
    embed.set_author(name='Help', icon_url='https://cdn.discordapp.com/attachments/501594682820788224/558396074868342785/UMass_Stem_discord_logo.png')
    embed.add_field(
        name = '-----------------------------------------------------------',
        value = '--------------------------ROLES--------------------------',
        inline = False
    )
    
    for command in ROLE_COMMANDS:
        embed.add_field(
            name = command,
            value = ROLE_COMMANDS[command],
            inline = False
        )

    embed.add_field(
        name = '-----------------------------------------------------------',
        value = '-------------------------GENERAL-------------------------',
        inline = False
    )
    for command in GENERAL_COMMANDS:
        embed.add_field(
            name = command,
            value = GENERAL_COMMANDS[command],
            inline = False
        )
    embed.set_footer(text='To see the meme and image filter commands use the $memehelp command')
    await ctx.send(embed=embed)

@client.command(name = 'memehelp')
async def meme_help(ctx):
    embed = discord.Embed(
        color = discord.Color.orange()
    )
    embed.set_author(name='Meme Help', icon_url='https://cdn.discordapp.com/attachments/501594682820788224/558396074868342785/UMass_Stem_discord_logo.png')
    MEME_COMMANDS = {
        '*$mdraw [image/url/text/nothing]*': 'Sends a photo of marius drawing the specified image or text',
        '*$tdraw [image/url/text/nothing]*': 'Sends a photo of tim drawing the specified image or text',
        '*$bdraw [image/url/text/nothing]*': 'Sends a photo of barrington drawing the specified image or text',
        '*$ldraw [image/url/text/nothing]*': 'Sends a photo of lan drawing the specified image or text',
        '*$landrew [image/url/text/nothing]*': 'Sends a photo of a different occasion of lan drawing the specified image or text',
        '*$shelpoint [image/url/text/nothing]*': 'Sends a photo of dan sheldon pointing to the specified image or text',
        '*barrify [image/url/nothing]*': 'The bot uses computer vision through the OpenCV library to put barrington on identified faces in the inputed image',
        '*surprisedpikachu [image/url/nothing]*': 'The bot uses computer vision through the OpenCV library to put surprised pikachu on identified faces in the inputed image',
        '*marify [image/url/nothing]*': 'The bot uses computer vision through the OpenCV library to put marius on identified faces in the inputed image',
        '*timify [image/url/nothing]*': 'The bot uses computer vision through the OpenCV library to put tim on identified faces in the inputed image',
        '*lanify [image/url/nothing]*': 'The bot uses computer vision through the OpenCV library to put lan on identified faces in the inputed image',
        '*liamify [image/url/nothing]*': 'The bot uses computer vision through the OpenCV library to put liam on identified faces in the inputed image',
        '*zoombarr [image/url/nothing]*': 'Pastes an image of barr from Zoom onto the given image in the top right corner',
        '*zoommar [image/url/nothing]*': 'Pastes an image of marius from Zoom onto the given image in the top right corner',
        '*zoomarun [image/url/nothing]*': 'Pastes an image of arun from Zoom onto the given image in the top right corner',
        '*$meme ["top" "bottom" image/url]*': 'The bot outputs the inputed image with the specified text in the old meme format',
        '*$okay* [image/url]':'The bot turns the given image into a video with marius saying okay as the background noise',
        '*$erase*': 'Deletes the most recent m/bdraw or barrify generated by the bot'
    }
    IMAGE_FILTER_COMMANDS = {
        '*$intensify [factor image]*': 'The bot outputs the inputed image intensified to the specified factor',
        '*$highlightEdge [image]*':'The bot outputs the inputed image with an edge highlighting algorithm applied to it',
        '*$customEdgeHighlight [Red Green Blue image]*':'The bot takes in RGB values (between 0 to 255) and applies an edge highlighting algorithm where the edges are the specified color',
        '*$noise [image]*':'The bot outputs the inputed image with a noise filter applied',
        '*$pixelate [factor image]*':'The bot outputs the inputed image after pixelating it by a given factor, remember to use a larger factor to see results on high-res images',
        '*$mirror [axis image]*':'The bot mirrors the image on the given axis (X or Y), and outputs the result',
        '*$saturate [factor image]*':'The bot saturates the given image by the given factor'
    }
    
    embed.add_field(
        name = '-----------------------------------------------------------',
        value = '--------------------------MEMES--------------------------',
        inline = False
    )
    for command in MEME_COMMANDS:
        embed.add_field(
            name = command,
            value = MEME_COMMANDS[command],
            inline = False
        )
    embed.add_field(
        name = '-----------------------------------------------------------',
        value = '----------------------IMAGE FILTERS----------------------',
        inline = False
    )
    for command in IMAGE_FILTER_COMMANDS:
        embed.add_field(
            name = command,
            value = IMAGE_FILTER_COMMANDS[command],
            inline = False
        )
    embed.set_footer(text='If no argument specified for draw, ify, and zoom commands the bot will use the last image outputted by the bot')
    await ctx.send(embed=embed)

@client.command(name = 'leaderboard')
async def display_leaderboard(ctx):
    channel_mentions = ctx.message.channel_mentions
    if len(channel_mentions) < 1:
        data = shelve.open('server-data/stem-discord-data')
        top_10 = get_top_10(data)        
        data.close()
        location = 'Server'
    elif len(channel_mentions) == 1:
        channel = channel_mentions[0]
        channel_activity_dict = dict()
        channel_activity_dict['Total Messages'] = 0
        async with ctx.channel.typing():
            async for message in channel.history(limit=100000):
                    try:
                        if (BOT_ROLE not in [role.name.lower() for role in message.author.roles]):
                            if str(message.author) in channel_activity_dict:
                                channel_activity_dict[str(message.author)] += 1
                            else:
                                channel_activity_dict[str(message.author)] = 1
                    except:
                        pass
                    channel_activity_dict['Total Messages'] += 1
            top_10 = get_top_10(channel_activity_dict)
            location = '#' + channel.name

    else:
        await ctx.send(embed=discord.Embed(description='Leaderboard only supports one channel at this time.', color=discord.Color.red()))
        return

    await ctx.send(embed=discord.Embed(title=location + ' Message Leaderboard', description=top_10, color=discord.Color.purple()))

def get_top_10(data):
    top_10 = ''
    number = 0
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
    return top_10

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
    await ctx.send('There are ' + str(ctx.message.guild.member_count) + ' server members')

@client.command(name = 'stats')
async def statistics(ctx):
    """Command to get the requested role's statistics including count

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await stem_role_commands.stats(ctx)

@client.command(name = 'covid19', aliases = ['corona', 'covid', 'coronavirus'])
async def covid(ctx):
    """Command to generate coronavirus statistics

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
        - args: optional, if state is passed in return the states cases and deaths, if nothing then return the top 15
    """
    await corona.coronavirus(ctx, False)

@client.command(name = 'covid19p', aliases = ['coronap', 'covidp', 'coronavirusp'])
async def covidp(ctx):
    """Command to generate coronavirus statistics sorted by percentage infected

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
        - args: optional, if state is passed in return the states cases and deaths, if nothing then return the top 15
    """
    print('running')
    await corona.coronavirus(ctx, True)

# vvv ROLE COMMANDS vvv

@client.command(name='get')
async def get_role(requested_role):
    """Command to get the requested role

       Args:
        - requested_role: context that the command occured use this to access the message and other attributes
    """
    member = requested_role.author
    channel = requested_role.channel
    if requested_role.guild.id == 387465995176116224:
        if requested_role.channel.id == 705669448421343282 or requested_role.channel.id == 705668942038958130:
            await stem_role_commands.stem_add_role(requested_role, member, client)
        else:
            message = await channel.send(embed=discord.Embed(description="In order to decrease spam, role commands are restricted to #role-assignment\nThis message will auto-delete in 15 seconds", color=discord.Color.dark_red()))
            await message.delete(delay=15)
            await requested_role.message.delete(delay=15)
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
        if requested_role.channel.id == 705669448421343282 or requested_role.channel.id == 705668942038958130:
            await stem_role_commands.stem_remove_role(requested_role, member, client)
        else:
            message = await channel.send(embed=discord.Embed(description="In order to decrease spam, role commands are restricted to #role-assignment\nThis message will auto-delete in 15 seconds", color=discord.Color.dark_red()))
            await message.delete(delay=15)
            await requested_role.message.delete(delay=15)
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

## vvv STOCK COMMANDS vvv

@client.command(name='stockcandle')
async def stock_candle(ctx, ticker, timeframe):
    await ctx.channel.send(embed=discord.Embed(description="Stock commands have been moved to the Discord Stock Exchange Bot.\nPlease use %stockcandle instead.", color=discord.Color.red()))

@client.command(name='stockline')
async def stock_line(ctx, ticker, timeframe):
    await ctx.channel.send(embed=discord.Embed(description="Stock commands have been moved to the Discord Stock Exchange Bot.\nPlease use %stockline instead.", color=discord.Color.red()))

@client.command(name='stock')
async def stock_price(ctx, ticker):
    await ctx.channel.send(embed=discord.Embed(description="Stock commands have been moved to the Discord Stock Exchange Bot.\nPlease use %stock instead.", color=discord.Color.red()))


# vvv MEME COMMANDS vvv
@client.command(name='mdraw')
async def mdraw(ctx):
    """Command to generate a meme of marius drawing on the image or text or gif

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await custom_meme.draw_universal(ctx,'memes/marius/draw.png', 7, overlay.marius_origin, 'marius-drawing')

@client.command(name='bdraw', aliases = ['barrdraw', 'barringtondraw'])
async def bdraw(ctx):
    """Command to generate a meme of barr drawing on the image or text or gif

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await custom_meme.draw_universal(ctx, 'memes/barrington/bdraw.png', 7, overlay.barr_origin, 'barrington-drawing')

@client.command(name='tdraw', aliases = ['timdraw', 'timrichardsdraw'])
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

@client.command(name='landrew', aliases = ['andrewlandrew'])
async def landrew(ctx):
    """Command to generate a meme of lan drawing on the image or text

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await custom_meme.draw_universal(ctx, 'memes/lan/landrew.png', 9, overlay.landrew_origin, 'landrew-drawing')

@client.command(name='shelpoint', aliases = ['sheldonpoint'])
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
        await custom_meme.bot_last_command[ctx.author.id].delete()
        custom_meme.bot_last_command[ctx.author.id] = None #Clears this back up to avoid errors

@client.command(name='barrify', aliases = ['barify', 'barringtonify', 'barry-ify'])
async def barrify(ctx, *args):
    """Command to paste barr's face on top of faces in an inputed image using facial recognition

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await custom_meme.ify(ctx, face_detection.barr_scale, 'memes/barrington/barr-face.png', 'barrify.png', args)

@client.command(name='liamify')
async def liamify(ctx, *args):
    """Command to paste liam's face on top of faces in an inputed image using facial recognition

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await custom_meme.ify(ctx, face_detection.liam_scale, 'memes/liam-head.png', 'liamify.png', args)

@client.command(name='marify', aliases = ['marrify', 'marius-ify'])
async def marify(ctx, *args):
    """Command to paste marius' face on top of faces in an inputed image using facial recognition

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await custom_meme.ify(ctx, face_detection.mar_scale, 'memes/marius/marius-face.png', 'marify.png', args)

@client.command(name='timify', aliases = ['tify', 'tim-ify'])
async def timify(ctx, *args):
    """Command to paste tim's face on top of faces in an inputed image using facial recognition

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await custom_meme.ify(ctx, face_detection.tim_scale, 'memes/tim/tim-face.png', 'timify.png', args)

@client.command(name='lanify', aliases = ['lan-ify'])
async def lanify(ctx, *args):
    """Command to paste lan's face on top of faces in an inputed image using facial recognition

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await custom_meme.ify(ctx, face_detection.lan_scale, 'memes/lan/lan-face.png', 'lan-face.png', args)

@client.command(name='surprisedpikachu', pass_context=True)
async def surprisedpikachu_overlay(ctx, *args):
    """Command to paste suprised pikachu on top of faces in an inputed image using facial recognition

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await custom_meme.ify(ctx, face_detection.sp_scale, 'memes/surprised-pikachu.png', 'surprisedpikachu.png', args)

@client.command(name='zoombarr', aliases=['streamerbarr', 'zoom-barr', 'zoombarrington', 'zoom-barrington'])
async def zoombarr(ctx, *args):
    """Command to paste an image of barr from Zoom onto the given image in the top right corner

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await custom_meme.zoomcam(ctx, 'memes/barrington/zoombarr.png', 'zoombarr_final.png', args)

@client.command(name='zoommar', aliases=['streamermarius', 'zoommarius', 'zoom-marr', 'zoom-mar', 'zoom-marius'])
async def zoommarius(ctx, *args):
    """Command to paste an image of marius from Zoom onto the given image in the top right corner

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await custom_meme.zoomcam(ctx, 'memes/marius/zoommarius.png', 'zoommarius_final.png', args)

@client.command(name='zoomarun', aliases=['streamerarun', 'zoom-arun', 'zoom-adunna', 'zoomadunna'])
async def zoomarun(ctx, *args):
    """Command to paste an image of arun from Zoom onto the given image in the top right corner

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    await custom_meme.zoomcam(ctx, 'memes/arun/zoom-arun.png', 'zoomarun_final.png', args)

@client.command(name='meme', pass_context=True)
async def meme_generator(ctx, *args):
    """Command to generate memes with top and bottom text

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
        - *args: arguments passed in with the command
    """
    channel = ctx.channel
    url = overlay.get_image_url_args(ctx.message, args, 3, 2)
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
        return
    custom_meme.track_command(ctx.author.id, message)
    os.remove('meme.png')

# vvv IMAGE FILTER COMMANDS vvv

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
        url = overlay.get_image_url_args(ctx.message, args, 2, 1)
    except:
        factor = 2 # default if no factor specified
        url = overlay.get_image_url_args(ctx.message, args, 1, 0)    
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
        return
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
        url = overlay.get_image_url_args(ctx.message, args, 2, 1)
        axis = args[0]
    except:
        await channel.send(embed=discord.Embed(description="Invalid input", color=discord.Color.red()))
        return
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
            return
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
            return
        custom_meme.track_command(ctx.author.id, message)
        os.remove("mirror_y.png")

@client.command(name='highlightEdge', aliases=['highlight', 'edge'])
async def highlight_edge(ctx, *args):
    """Command to apply an edge highlighting algorithm to a given image

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    channel = ctx.channel
    url = overlay.get_image_url_args(ctx.message, args, 1, 0)
    if url == 0:
        await channel.send(embed=discord.Embed(description="Invalid Image"), color=discord.Color.red())
        return
    output = filters.highlight_image(overlay.url_to_image(url))
    output.save('highlighted.png')
    try:
        message = await channel.send(file=discord.File('highlighted.png'))
    except:
        message = await channel.send(embed=discord.Embed(description="Image too large", color=discord.Color.red()))
        return
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
    url = overlay.get_image_url_args(ctx.message, args, 4, 3)
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
        return
    custom_meme.track_command(ctx.author.id, message)
    os.remove('custom_highlight.png')

@client.command(name='noise', pass_context=True)
async def noise_filter(ctx):
    """Command to apply a noise filter on the inputted image

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    channel = ctx.channel
    url = overlay.get_image_url(ctx.message, 7)
    if url == 0:
        await channel.send(embed=discord.Embed(description="Invalid Image", color=discord.Color.red()))
        return
    output = filters.scramble_pixels(overlay.url_to_image(url))
    output.save('noise.png')
    try:
        message = await channel.send(file=discord.File('noise.png'))
    except:
        message = await channel.send(embed=discord.Embed(description="Image too large", color=discord.Color.red()))
        return
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
    url = overlay.get_image_url_args(ctx.message, args, 2, 1)
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
        return
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
    url = overlay.get_image_url_args(ctx.message, args, 2, 1)
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
        return
    custom_meme.track_command(ctx.author.id, message)
    os.remove('saturate.png')

@client.command(name='okay', pass_context=True)
async def make_okay(ctx):
    """Command to turn a given image into a video where marius says 'okay' in the background

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    channel = ctx.channel
    url = overlay.get_image_url(ctx.message, 6)
    if url == 0:
        await channel.send(embed=discord.Embed(description="Invalid Image", color=discord.Color.red()))
        return
    clip = filters.make_okay_clip(overlay.url_to_image(url))
    clip.write_videofile("okay.mp4", audio= "sfx/okayturnedupto8.mp3", fps=24)
    try:
        message = await channel.send(file=discord.File("okay.mp4"))
    except:
        message = await channel.send(embed=discord.Embed(description="Image too large", color=discord.Color.red()))
        return
    custom_meme.track_command(ctx.author.id, message)
    os.remove("okay.mp4")

client.run(BOT_TOKEN)
