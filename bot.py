import random
from io import BytesIO
from pathlib import Path
import discord
from discord.ext.commands import Bot
import asyncio
from overlay import overlay_image
from overlay import url_to_image
import os
import time

BOT_PREFIX = "$"
BOT_TOKEN = os.environ.get('BOT_TOKEN')
HOUSING_ROLE_IDS = {'Alumni': '501529720932925441', 
                    'Sylvan': '444332276483096586', 
                    'OHill': '444332646307201034', 
                    'Central': '444332880894754818', 
                    'Southwest': '444332735838814210', 
                    'Northeast': '444332948322517003', 
                    'North Apts': '444588763427897344', 
                    'Honors College': '444333125670010890', 
                    'Off-Campus': '405025553448566795', 
                    'Prospective Student': '524016335299280908'
} 

MAJOR_ROLE_IDS = {'Electrical Engineering': '442786317273792523', 
                  'Comp-Engineering': '506504010585604132', 
                  'Chemical Engineering': '504715524152754199', 
                  'Biomedical Engineering': '506504177242079241', 
                  'Environmental-Engineering': '442806923025186817', 
                  'Civil Engineering': '506211361945288735', 
                  'Industrial and Mechanical Engineering': '501524792436981791', 
                  'ECE': '439552642415460353', 
                  'Computer Science': '387619060633829377', 
                  'Environmental Science': '442784019369951252', 
                  'Mathematics': '442785279493799966',
                  'Economics': '387670593987805184',
                  'Informatics': '405032140040830998',
                  'Information Technology': '506223375056633856',
                  'Political Science': '405035782269829121',
                  'Biology': '442784136457879567',
                  'Plant Science': '442784769273626626',
                  'Food Science': '506253630714806272',
                  'Geology': '442822241135230978',
                  'History': '443558312794128407',
                  'Physics': '447463828398145537',
                  'BDIC': '536247576496701440',
                  'Communication': '405932216808505355',
                  'Nutrition': '490210619270889486',
                  'Biochemistry': '501525484257935360',
                  'Microbiology': '501608246579167233',
                  'Animal Science': '502556060171894785',
                  'Animation': '502624207390244864',
                  'Business': '507634130842812441',
                  'Accounting': '509005908072726533',
                  'Linguistics': '517414427390378041',
                  'Comparative Literature': '551464859301314572',
                  'Chinese': '522165967481208833',
                  'Japanese': '522166045939597335',
                  'Psychology': '524039481486213151',
                  'Public Health': '543109471136645161',
                  'Women, Gender, and Sexuality Studies': '541744140191268894',
                  'Education': '524777786972307477',
                  'English': '539870761754820628',
                  'CICS Exploratory': '387619488880787457',
                  'Engineering-Undecided': '506211413564325919',
                  'Undecided': '501908170654875648'
}
                   
client = Bot(command_prefix=BOT_PREFIX)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    member = message.author
    if message.server.id == '387465995176116224' and "missing housing or major role" in [role.name.lower() for role in member.roles]: #UMass Amherst STEM
        member_has_hr = False
        member_has_m = False
        time.sleep(6)
        for role in member.roles:
            if role.name.lower() == 'missing housing or major role':
                mhom = role
            if role.id in HOUSING_ROLE_IDS.values():
                member_has_hr = True
            if role.id in MAJOR_ROLE_IDS.values():
                member_has_m = True
        if member_has_hr and member_has_m:
            await client.remove_roles(member, mhom) #removes missing housing or major role

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

client.run(BOT_TOKEN)
