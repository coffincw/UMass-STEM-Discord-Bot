import random
from io import BytesIO
import discord
from discord.ext.commands import Bot
import asyncio
from overlay import overlay_image
from overlay import url_to_image
import os

BOT_PREFIX = "$"
BOT_TOKEN = "NTUyMjU0NTk4Mjc5MDY5NzA4.D1823Q.77zzMatjVJRQ0OmyOENOheYS03w"

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

@client.command(name='draw', pass_context = True)
async def draw(ctx):
    image_url = ''
    # try:
    #     image = message.attachments[0]['url']
    # except IndexError:
    #     extension = ['.jpg', '.png', '.jpeg']
    #     for ext in extension:
    #         if message.content.endswith(ext):
    #             image = message.content
    #     if (image == ''):
    #         await client.say("Please input a valid image")
    image_url = ctx.message.attachments[0]['url']
    image = url_to_image(image_url)
    image.show()
    output = overlay_image(image, 'C:/Users/Caleb/Documents/Programming-Projects/UMassMemeBot/memes/marius/draw.png')
    if output == 0:
        return
    
    output.show()
    output.save('temp.png')
    await client.send_file(ctx.message.channel, 'temp.png')
    os.remove('temp.png')
    # await client.send_file(ctx.message.channel, output)


@client.command()
async def square(number):
    await client.say(str(number) + " squared is " + str(int(number) * int(number)))


print("Test")

# client.loop.create_taks(list_servers())
client.run(BOT_TOKEN)