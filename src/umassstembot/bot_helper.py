import discord
import asyncio


async def del_convo(user_msg, bot_msg, delay):
    """
    Deletes both the user and bot message after the specified delay in seconds

    Parameters:
    - user_msg: message object for the user's message
    - bot_msg: message object for the bot's message
    - delay: int representing the number of seconds to delay before deleting
    """
    await bot_msg.delete(delay=delay)
    await user_msg.delete(delay=delay)
