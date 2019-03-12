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
BOT_TOKEN = os.environ.get('BOT_TOKEN')
HOUSING_ROLE_IDS = {'Alumni': 501529720932925441, 
                    'Sylvan': 444332276483096586, 
                    'OHill': 444332646307201034, 
                    'Central': 444332880894754818, 
                    'Southwest': 444332735838814210, 
                    'Northeast': 444332948322517003, 
                    'North Apts': 444588763427897344, 
                    'Honors College': 444333125670010890, 
                    'Off-Campus': 405025553448566795, 
                    'Prospective Student': 524016335299280908
} 

MAJOR_ROLE_IDS = {'Electrical Engineering': 442786317273792523, 
                  'Comp-Engineering': 506504010585604132, 
                  'Chemical Engineering': 504715524152754199, 
                  'Biomedical Engineering': 506504177242079241, 
                  'Environmental-Engineering': 442806923025186817, 
                  'Civil Engineering': 506211361945288735, 
                  'Industrial and Mechanical Engineering': 501524792436981791, 
                  'ECE': 439552642415460353, 
                  'Computer Science': 387619060633829377, 
                  'Environmental Science': 442784019369951252, 
                  'Mathematics': 442785279493799966 
}
                   

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
async def on_message(message):
    member = message.author

    member_has_hr = False
    member_has_m = False
    for role in member.roles:
        if member.roles[role] in HOUSING_ROLE_IDS:
            member_has_hr = True
        if member.roles[role] in MAJOR_ROLE_IDS:
            member_has_m = True
    if member_has_hr and member_has_m:
        await client.remove_roles(member, 444868818997608460) #removes missing housing or major role

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

# client.loop.create_taks(list_servers())
client.run(BOT_TOKEN)
