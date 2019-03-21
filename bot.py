import random
from io import BytesIO
from pathlib import Path
import discord
from discord import Game
from discord.ext.commands import Bot
import asyncio
from overlay import overlay_image
from overlay import url_to_image
import os
import time

BOT_PREFIX = "$"
BOT_TOKEN = os.environ.get('BOT_TOKEN')

BOT_ROLE = "bots"

HOUSING_ROLE_IDS = {'501529720932925441', ['alumni', 'alum', 'alumn'],
                    '444332276483096586', ['sylvan', 'syl'],
                    '444332646307201034', ['ohill', 'orchard hill', 'o hill'],
                    '444332880894754818', ['central'], 
                    '444332735838814210', ['southwest', 'sw', 'swest'],
                    '444332948322517003', ['northeast', 'ne'],
                    '444588763427897344', ['north apts', 'north apartments', 'north apartment'], 
                    '444333125670010890', ['honors college'],
                    '405025553448566795', ['off-campus', 'off campus', 'offcampus', 'commute', 'commuter'],
                    '524016335299280908', ['prospective student', 'hs', 'high school']
}

MAJOR_ROLE_IDS = {'442786317273792523', ['electrical engineering', 'ee', 'electrical-engineering'],
                  '506504010585604132', ['computer engineering', 'ce', 'comp-engineering', 'computer-engineering'],
                  '504715524152754199', ['biomedical engineering', 'be', 'bio-engineering'],
                  '506504177242079241', ['environmental engineering', 'environmental-engineering'],
                  '506211361945288735', ['civil engineering', 'civil-engineering'],
                  '501524792436981791', ['industrial and mechanical engineering', 'ime', 'industrial engineering', 'me', 'ie', 'mechanical engineering', 'industrial mechanical engineering'],
                  '439552642415460353', ['ece', 'electrical and computer engineering', 'ec engineering'],
                  '387619060633829377', ['computer science', 'cs', 'compsci', 'comp-sci'],
                  '442784019369951252', ['environmental science', 'es'],
                  '442785279493799966', ['math', 'mathematics'],
                  '387670593987805184', ['economics', 'econ'],
                  '405032140040830998', ['informatics', 'info'],
                  '506223375056633856', ['information technology', 'information tech', 'it'],
                  '405035782269829121', ['political science', 'polisci', 'poli-sci'],
                  '442784136457879567', ['biology', 'bio'],
                  '442784769273626626', ['plant science'], 
                  '442822241135230978', ['geology', 'geo'], 
                  '506253630714806272', ['food science'],
                  '443558312794128407', ['history'],
                  '447463828398145537', ['physics'],
                  '536247576496701440', ['bdic', 'bachelors degree with individual concentration'],
                  '405932216808505355', ['communications', 'communication', 'comm', 'com'],
                  '490210619270889486', ['nutrition'],
                  '501525484257935360', ['biochemistry', 'biochem'],
                  '501608246579167233', ['microbiology', 'microbio'],
                  '502556060171894785', ['animal science', 'animal'],
                  '502624207390244864', ['animation'],
                  '507634130842812441', ['business', 'isenberg'],
                  '509005908072726533', ['accounting', 'account'],
                  '517414427390378041', ['linguistics', 'ling'],
                  '551464859301314572', ['comparative literature', 'comp lit', 'comp-lit'],
                  '522165967481208833', ['chinese'],
                  '522166045939597335', ['japanese'],
                  '524039481486213151', ['psychology', 'psych'],
                  '543109471136645161', ['public health', 'pub health', 'pub hlth'],
                  '541744140191268894', ['women, gender, and sexuality studies'],
                  '524777786972307477', ['education', 'educ'],
                  '539870761754820628', ['english'],
                  '387619488880787457', ['cics exploratory', 'cs exploratory', 'cs explo', 'exploratory computer science', 'computer science exploratory', 'exporatory cs', 'exploratory'], 
                  '506211413564325919', ['engineering undecided', 'engineering-undecided', 'undecided engineering', 'engineering'],
                  '501908170654875648', ['undecided']
}
                   
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


@client.event
async def on_message(message):
    member = message.author
    if message.server.id == '387465995176116224' and "missing housing or major role" in [role.name.lower() for role in member.roles]: #UMass Amherst STEM
        member_has_hr = False
        member_has_m = False
        # time.sleep(20)
        for role in member.roles:
            if role.name.lower() == 'missing housing or major role':
                mhom = role
            if role.id in HOUSING_ROLE_IDS:
                member_has_hr = True
            if role.id in MAJOR_ROLE_IDS:
                member_has_m = True
        if member_has_hr and member_has_m:
            await client.remove_roles(member, mhom) #removes missing housing or major role
    await client.process_commands(message)

@client.command(name='get')

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

@client.command(name='get', pass_context = True)
async def get_role(ctx):
    print("s")

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
