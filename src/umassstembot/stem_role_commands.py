import discord
import asyncio
from stem_server_roles import HOUSING_ROLE_IDS, MAJOR_ROLE_IDS, CLASS_ROLE_IDS, GRAD_YEAR_ROLE_IDS, SPECIAL_ROLE_IDS
from discord.utils import get

def merge_dict(dicts): # merges dictionaries together
    z = dicts[0].copy()
    for i in range(1, len(dicts)):
        z.update(dicts[i])
    return z

def capitalize_all_words(in_str):
    words = in_str.split()
    output = ''
    for word in words:
        output += word.capitalize() + ' '
    return output[:-1]

async def list_roles(ctx, client):
    getlist = discord.Embed(color=discord.Color.blue())
    getlist.set_author(name='Roles | Use $get [role] to add a role', icon_url='https://cdn.discordapp.com/attachments/501594682820788224/558396074868342785/UMass_Stem_discord_logo.png')
    housing_role_list = ''
    housing_roles = sorted(HOUSING_ROLE_IDS.values(), key=lambda x: x[0])
    for role in housing_roles:
        housing_role_list += capitalize_all_words(role[0]) + '\n'
    getlist.add_field(name = 'Housing Roles', value=housing_role_list, inline=False)
    major_role_list = ''
    major_roles = sorted(MAJOR_ROLE_IDS.values(), key=lambda x: x[0])
    for role in major_roles:
        major_role_list += capitalize_all_words(role[0]) + '\n'
    getlist.add_field(name = 'Major Roles', value=major_role_list, inline=False)
    grad_role_list = ''
    for role in GRAD_YEAR_ROLE_IDS.values():
        grad_role_list += capitalize_all_words(role[0]) + '\n'
    getlist.add_field(name = 'Graduation Year Roles', value=grad_role_list, inline=False)
    class_role_list = ''
    for role in CLASS_ROLE_IDS.values():
        name = role[0].upper()
        if class_role_list == '':
            class_role_list += '**Computer Science**\n'
        if name.startswith('CS') or name.startswith('CICS'):
            class_role_list += name + ', '
            continue
        if name.endswith('127'):
            class_role_list = class_role_list[:len(class_role_list)-2] # trim last ', '
            class_role_list += '\n**Mathematics**\n'
        if name.startswith('MATH') or name.startswith('STATS'):
            class_role_list += name + ', '
            continue
        if name.endswith('499'):
            class_role_list = class_role_list[:len(class_role_list)-2] # trim last ', '
            class_role_list += '\n**Other**\n'
        class_role_list += name + ', '
    class_role_list = class_role_list[:len(class_role_list)-2] # trim last ', '
    getlist.add_field(name = 'Class Specific Roles', value=class_role_list, inline=False)
    getlist.set_footer(text='If you want a role added to the server @Caleb or suggest it in #suggestions')
    await ctx.channel.send(embed=getlist)

async def list_my_roles(ctx, client, member):
    housing_roles, major_roles, graduation_year = '', '', ''
    class_specific_roles, special_roles = [], []
    
    for role in sorted(member.roles, key=lambda x: x.name):
        name = capitalize_all_words(role.name)
        if role.id in HOUSING_ROLE_IDS:
            housing_roles += name + '\n'
        if role.id in MAJOR_ROLE_IDS:
            major_roles += name + '\n'
        if role.id in CLASS_ROLE_IDS:
            class_specific_roles.append(role.name.upper())
        if role.id in GRAD_YEAR_ROLE_IDS:
            graduation_year = name + '\n'
        if role.id in SPECIAL_ROLE_IDS:
            special_roles.append(name)

    # add class roles in alphabetic order
    class_specific = ''
    class_specific_roles = sorted(class_specific_roles)
    for role in class_specific_roles:
        class_specific += role + '\n'
    
    # add special roles in alphabetic order
    special = ''
    special_roles = sorted(special_roles)
    for role in special_roles:
        special += role + '\n'

    if special is not '':
        mylist = discord.Embed(color=0xb5a2c8, description= '**' + special + '**')
    else:
        mylist = discord.Embed(color=0xb5a2c8)
    mylist.set_author(name = '' + member.name + '\'s roles', icon_url = member.avatar_url)

    if housing_roles == '':
        mylist.add_field(name = 'Housing Roles', value='Missing housing role, set your residential area role in #role-assignment', inline=False)
    else:
        mylist.add_field(name = 'Housing Roles', value=housing_roles, inline=False)
    if major_roles == '':
        mylist.add_field(name = 'Major Roles', value='Missing major role, set at least one major/minor role in #role-assignment', inline=False)
    else:
        mylist.add_field(name = 'Major Roles', value=major_roles, inline=False)
    if class_specific != '':
        mylist.add_field(name = 'Class Roles', value=class_specific, inline=False)
    if graduation_year != '':
        mylist.add_field(name = 'Graduation Year', value=graduation_year, inline=False)
    await ctx.channel.send(embed=mylist)    

async def stats(ctx):
    contents = ctx.message.content[6:].strip().lower()
    if len(contents) == 0:
        await ctx.send(embed=discord.Embed(description='You must specify a valid role, for example: $stats Computer Science', color=discord.Color.red()))
        return
    possible_roles = merge_dict([HOUSING_ROLE_IDS, MAJOR_ROLE_IDS, CLASS_ROLE_IDS, GRAD_YEAR_ROLE_IDS, SPECIAL_ROLE_IDS])
    found = False
    for role_id, role_names in possible_roles.items():
        for alias in role_names:
            if contents == alias: # valid role
                found = True
                role = get(ctx.guild.roles, id=role_id)
                break
    if not found:
        await ctx.send(embed=discord.Embed(description='Invalid role specified. You must specify a valid role, for example: $stats Computer Science', color=discord.Color.red()))
        return      
    await ctx.send(embed=discord.Embed(title=role.name + ' Role Statistics', description = 'Count: ' + str(len(role.members)), color=discord.Color.greyple()))

async def stem_add_role(requested_role, member, client):
    channel = requested_role.channel
    available_roles = merge_dict([HOUSING_ROLE_IDS, MAJOR_ROLE_IDS, CLASS_ROLE_IDS, GRAD_YEAR_ROLE_IDS])
    role_lower = requested_role.message.content[5:].lower().strip().replace('[', '').replace(']', '')
    is_grad_role = False

    #check if user already has a graduation role
    for role in member.roles:
        for grad_years in GRAD_YEAR_ROLE_IDS.values():
            if role.name.lower() in grad_years:
                is_grad_role = True

    for role_names in available_roles.values():
        for alias in role_names:
            if role_lower == alias: # valid role

                # check if member already has the requested role
                for member_role in member.roles:
                    if member_role.name.lower() == role_names[0]:
                        await channel.send(embed=discord.Embed(description="I'm sorry, " + member.name + ", you already have this role!\nUse the $remove [role] command to remove it!", color=discord.Color.gold()))
                        return

                # if the member doesnt already have the requested role
                for role in requested_role.message.guild.roles:
                    if role.name.lower() == role_names[0]:
                        role_to_add = role
                        
                # make sure member isn't trying to add a second grad year role, they should only be allowed to have one
                for grad_year_roles in GRAD_YEAR_ROLE_IDS.values():
                    if role_to_add.name.lower() in grad_year_roles and is_grad_role:
                        await channel.send(embed=discord.Embed(description="I'm sorry, " + member.name + ", you already have a graduation year role!\nUse the $remove [role] command to remove it in order to add a different one!", color=discord.Color.gold()))
                        return

                await member.add_roles(role_to_add)
                await asyncio.sleep(1)
                await check_major_housing_role(member, client)
                await channel.send(embed=discord.Embed(description="Added " + role_to_add.name + " to " + member.name + "\nUse the $remove [role] command to remove it!", color=discord.Color.green()))
                return
    await channel.send(embed=discord.Embed(description="I'm sorry, " + member.name + ", there is no role with that name!\nUse the $getlist command to see the available roles", color=discord.Color.red()))

async def check_major_housing_role(member, client):
    member_has_hr = False
    member_has_m = False
    for role in member.roles:
        if role.id in HOUSING_ROLE_IDS:
            member_has_hr = True
        if role.id in MAJOR_ROLE_IDS:
            member_has_m = True
    for role in member.guild.roles:
        if role.name.lower() == 'missing housing or major role':
            mhom = role
    if mhom in member.roles: # check if the member has the missing housing or major role
        if member_has_hr and member_has_m:
            await member.remove_roles(mhom) #removes missing housing or major role
    else: # if not then add it to them if they need it
        if not member_has_hr or not member_has_m:
            await member.add_roles(mhom) #adds missing housing or major role if they dont have the roles

async def stem_remove_role(requested_role, member, client):
    channel = requested_role.channel
    removable_roles = merge_dict(HOUSING_ROLE_IDS, MAJOR_ROLE_IDS, CLASS_ROLE_IDS, GRAD_YEAR_ROLE_IDS)
    role_lower = requested_role.message.content[8:].lower().strip().replace('[', '').replace(']', '')
    for role in member.roles:
        if role.id in removable_roles.keys() and role_lower in removable_roles[role.id]:
            for housing_major_role in removable_roles.values():
                for alias in housing_major_role:
                    if role_lower == alias:
                        await member.remove_roles(role)
                        await asyncio.sleep(1)
                        await check_major_housing_role(member, client)
                        await channel.send(embed=discord.Embed(description="Removed " + role.name + " from " + member.name, color=discord.Color.green()))
                        return
            await channel.send(embed=discord.Embed(description="I'm sorry, " + member.name + ", you can't remove that role", color=discord.Color.red()))
            return
    await channel.send(embed=discord.Embed(description="I'm sorry, " + member.name + ", you don't have a role with that name", color=discord.Color.red()))
