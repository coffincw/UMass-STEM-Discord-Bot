import random
from io import BytesIO
from pathlib import Path
import discord
from discord import Game
from discord.ext.commands import Bot
import asyncio
from overlay import overlay_image, url_to_image
from stem_roles import HOUSING_ROLE_IDS, MAJOR_ROLE_IDS, stem_add_role, stem_remove_role
import os
import time

BOT_PREFIX = "$"
BOT_TOKEN = os.environ.get('BOT_TOKEN')

BOT_ROLE = "bots"


                   
client = Bot(command_prefix=BOT_PREFIX)


@client.event
async def on_ready():
    await client.change_presence(game = Game(name = '#rules'))
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message_delete(message):
    author = message.author
    if message.server.id == '387465995176116224':
        if (BOT_ROLE not in [role.name.lower() for role in author.roles]):
            content = message.content
            await client.send_message(client.get_channel('557002016782680076'), '_Deleted Message_\n**Message sent by:** ' + author.mention + '\n**Channel:** ' + message.channel.mention + '\n**Contents:** *' + content + '*\n--------------')

@client.event
async def on_message_edit(before, after):
    author = before.author
    if before.server.id == '387465995176116224':
        if (BOT_ROLE not in [role.name.lower() for role in author.roles]):
            before_content = before.content
            after_content = after.content
            await client.send_message(client.get_channel('557002016782680076'), '_Edited Message_\n**Message sent by:** ' + author.mention + '\n**Channel:** ' + before.channel.mention + '\n**Pre-edit contents:** *' + before_content + '*\n**Post-edit contents:** *'+ after_content + '*\n--------------')

@client.command(name='8ball',
                description="Answers from the 8ball",
                pass_context = True)
async def eight_ball(context):
    print("test")
    possible_responses = [
        'That is a resounding no',
        'It is not looking likely',
        'Too hard to tell'
    ]
    await client.say(random.choice(possible_responses))

def merge_dict(x, y):
    z = x.copy()
    z.update(y)
    return z

@client.command(name='get', pass_context = True)
async def get_role(requested_role):
    member = requested_role.message.author
    if requested_role.message.server.id == '387465995176116224':
        await stem_add_role(requested_role, member, client)
    else:
        await client.send_message(requested_role.message.channel, embed=discord.Embed(description="Roles are not yet supported on this server", color=discord.Color.dark_red()))

@client.command(name='remove', pass_context = True)
async def remove_role(requested_role):
    member = requested_role.message.author
    if requested_role.message.server.id == '387465995176116224':
        await stem_remove_role(requested_role, member, client)
    else:
        await client.send_message(requested_role.message.channel, embed=discord.Embed(description="Roles are not yet supported on this server", color=discord.Color.dark_red()))

# add command to list gettable roles
# move checking whether missing a housing or major role to after get is called instead of every message

# @client.command(name'getlist', pass_context = True)
# async def getlist(ctx):
#     member = ctx.message.author
#     if ctx.message.server.id == '387465995176116224':


@client.command(name='mdraw', pass_context = True)
async def mdraw(ctx):
    url = get_image_url(ctx)
    if url == 0:
        await client.say("Please input a valid image")

    output = overlay_image(url_to_image(url), Path('memes/marius/draw.png'))
    name = 'marius-drawing.png'
    output.save(name)
    await client.send_file(ctx.message.channel, name)
    os.remove(name)

@client.command(name='bdraw', pass_context = True)
async def bdraw(ctx):
    url = get_image_url(ctx)
    if url == 0:
        await client.say("Please input a valid image")
    output = overlay_image(url_to_image(url), Path('memes/barrington/bdraw.png'))
    output.save('barrington-drawing.png')
    await client.send_file(ctx.message.channel, 'barrington-drawing.png')
    os.remove('barrington-drawing.png')
    

def get_image_url(ctx):
    image_url = ''
    try:
        image_url = ctx.message.attachments[0]['url']
    except:
        extension = ['.jpg', '.png', '.jpeg']
        for ext in extension:
            if ctx.message.content.endswith(ext):
                image_url = ctx.message.content[5:]
        if (image_url == ''):
            return 0
    return image_url
    
@client.command(name ='drawrec', pass_context = True) 
async def draw_loop(ctx):
    i = 5
    while (i > 0):
        ctx = get_image_url(ctx)
        i+=1
    mdraw(ctx)

@client.command(name='drawt', pass_context = True)
async def draw_on_text(ctx):
    # Allows the user to input text into the draw meme
    print("fill")

@client.command()
async def square(number):
    await client.say(str(number) + " squared is " + str(int(number) * int(number)))

client.run(BOT_TOKEN)
