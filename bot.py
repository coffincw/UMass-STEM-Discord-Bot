import random
from io import BytesIO
from pathlib import Path
import discord
from discord.ext.commands import Bot
import asyncio
from overlay import overlay_image
from overlay import url_to_image
import os

BOT_PREFIX = "$"


client = Bot(command_prefix=BOT_PREFIX)

@client.command(name='8ball',
                description="Answers from the 8ball",
                pass_context = True)
async def eight_ball(context):
    possible_responses = [
        'That is a resounding no',
        'It is not looking likely',
        'Too hard to tell'
    ]
    await client.say(random.choice(possible_responses))

# @client.event
# async def on_message(message):
#     print(message.attachments[0]['url'])

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


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

# client.loop.create_taks(list_servers())
client.run(BOT_TOKEN)
