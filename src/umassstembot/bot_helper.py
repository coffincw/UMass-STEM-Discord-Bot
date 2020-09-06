import discord
import asyncio


async def del_convo(user_msg, bot_msg, delay):
    await bot_msg.delete(delay=delay)
    await user_msg.delete(delay=delay)
