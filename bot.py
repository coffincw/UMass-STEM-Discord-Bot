import random
from io import BytesIO
from pathlib import Path
import discord
from discord import Game
from discord.ext.commands import Bot
import asyncio
from overlay import overlay_image, url_to_image, get_image_url, draw_text
from stem_roles import stem_add_role, stem_remove_role, list_roles
import os
import time

BOT_PREFIX = "$"
BOT_TOKEN = os.environ.get('BOT_TOKEN')

BOT_ROLE = "bots"
 
client = Bot(command_prefix=BOT_PREFIX)
client.remove_command('help')

@client.event
async def on_ready():
    await client.change_presence(game = Game(name = '#rules | $help'))
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

@client.command()
async def help():
    embed = discord.Embed(
        color = discord.Color.orange()
    )
    embed.set_author(name='Help', icon_url='https://cdn.discordapp.com/attachments/501594682820788224/558396074868342785/UMass_Stem_discord_logo.png')
    embed.add_field(name = 'Roles', value='*$getlist* - Sends a list of all the available roles\n*$get [role]* - Gives you the specified role\n*$remove [role]* - Removes the specified role from you', inline=True)
    embed.add_field(name = 'Memes', value='*$mdraw [image/url]* - Sends a photo of <:smugmarius:557699496767651840> drawing on the specified image\n*$bdraw [image/url]* - Sends a photo of <:barr:557186728167997445> drawing on the specified image', inline=True)
    await client.say(embed=embed)

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

@client.command(name='getlist', pass_context = True)
async def get_list(ctx):
    await list_roles(ctx, client) # found in stem_roles.py

@client.command(name='mdraw', pass_context = True)
async def mdraw(ctx):
    url = get_image_url(ctx)
    if url == 0:
        output = draw_text(ctx.message.content[7:], Path('memes/marius/draw.png'))
    else:
        output = overlay_image(url_to_image(url), Path('memes/marius/draw.png'))
    name = 'marius-drawing.png'
    output.save(name)
    await client.send_file(ctx.message.channel, name)
    os.remove(name)

@client.command(name='bdraw', pass_context = True)
async def bdraw(ctx):
    url = get_image_url(ctx)
    if url == 0:
        output = draw_text(ctx.message.content[7:], Path('memes/barrington/bdraw.png'))
    else:
        output = overlay_image(url_to_image(url), Path('memes/barrington/bdraw.png'))
    output.save('barrington-drawing.png')
    await client.send_file(ctx.message.channel, 'barrington-drawing.png')
    os.remove('barrington-drawing.png')
    
# @client.command(name ='drawrec', pass_context = True) 
# async def draw_loop(ctx):
#     i = 5
#     while (i > 0):
#         ctx = get_image_url(ctx)
#         i+=1
#     mdraw(ctx)

@client.command(name='drawt', pass_context = True)
async def draw_on_text(ctx):
    # Allows the user to input text into the draw meme
    print("fill")

@client.command()
async def square(number):
    await client.say(str(number) + " squared is " + str(int(number) * int(number)))

client.run(BOT_TOKEN)
