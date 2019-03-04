import random
from discord.ext.commands import Bot
import asyncio

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

@client.command(name='draw')
async def draw(message):
    extension = ['.jpg', '.png', '.jpeg']
    for ext in extension:
        if message.content.endswith(ext):
            

@client.command()
async def square(number):
    await client.say(str(number) + " squared is " + str(int(number) * int(number)))

async def list_servers():
    await client.wait_until_ready()
    while not client.is_closed:
        print("Current servers: ")
        for server in client.servers:
            print(server.name)
        await asyncio.sleep(6)


print("Test")

client.loop.create_taks(list_servers())
client.run(BOT_TOKEN)