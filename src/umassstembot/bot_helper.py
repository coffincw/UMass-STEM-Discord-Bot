import discord
import asyncio
from discord.utils import get

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

async def get_mhom(roles):
    """
    Returns the 'Missing Housing or Major Role' if the role list has the role

    Parameters:
    - member: roles list to check
    
    Returns:
    - role: 'Missing Housing or Major' role object, if the list doesn't have it then None is returned
    """
    return get(roles, id=444868818997608460) # Missing Housing or Major role id

async def contains_role(roles, name):
    """
    Checks if the role list contains a role with the name 'name'

    Parameters:
    - roles: list of role objects
    - name: name of role
    
    Returns:
    - role: role object that has the name 'name'
    """
    for r in roles:
        if r.name.lower() == name:
            return r