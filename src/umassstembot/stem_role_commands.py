import discord
import asyncio
from stem_server_roles import HOUSING_ROLE_IDS, MAJOR_ROLE_IDS, CLASS_ROLE_IDS, GRAD_YEAR_ROLE_IDS, SPECIAL_ROLE_IDS, PRONOUN_ROLE_IDS
from discord.utils import get
from bot_helper import del_convo

def merge_dict(dicts): # merges dictionaries together
    z = dicts[0].copy()
    for i in range(1, len(dicts)):
        z.update(dicts[i])
    return z

def capitalize_all_words(in_str, separator):
    words = in_str.split(separator)
    output = ''
    for word in words:
        output += word.capitalize() + separator
    return output[:-1]


async def list_roles(ctx, client):
    getlist = discord.Embed(color=discord.Color.blue())
    getlist.set_author(
        name='Roles | Use $get [role] in #role-assignment to add a role', 
        icon_url='https://cdn.discordapp.com/attachments/501594682820788224/558396074868342785/UMass_Stem_discord_logo.png')
    housing_role_list = ''
    for role in HOUSING_ROLE_IDS.values():
        housing_role_list += capitalize_all_words(role[0], ' ') + '\n'
    getlist.add_field(name = 'Housing Roles', value=housing_role_list, inline=False)
    major_role_list = ''
    for role in MAJOR_ROLE_IDS.values():
        major_role_list += capitalize_all_words(role[0], ' ') + '\n'
    getlist.add_field(name = 'Major Roles', value=major_role_list, inline=False)
    grad_role_list = ''
    for role in GRAD_YEAR_ROLE_IDS.values():
        grad_role_list += capitalize_all_words(role[0], ' ') + '\n'
    getlist.add_field(name = 'Graduation Year Roles', value=grad_role_list, inline=False)
    pronoun_role_list = ''
    for role in PRONOUN_ROLE_IDS.values():
        pronoun_role_list += capitalize_all_words(role[0], '/') + '\n'
    getlist.add_field(name = 'Pronoun Roles', value=pronoun_role_list, inline=False)
    class_role_list = ''
    for role in CLASS_ROLE_IDS.values():
        name = role[0].upper()
        if class_role_list == '':
            class_role_list += '__Computer Science__\n'
        if name.startswith('CS') or name.startswith('CICS'):
            class_role_list += name + ', '
            continue
        if name.endswith('127'):
            class_role_list = class_role_list[:len(class_role_list)-2] # trim last ', '
            class_role_list += '\n__Mathematics__\n'
        if name.startswith('MATH') or name.startswith('STATS'):
            class_role_list += name + ', '
            continue
        if name.endswith('499'):
            class_role_list = class_role_list[:len(class_role_list)-2] # trim last ', '
            class_role_list += '\n__Other__\n'
        class_role_list += name + ', '
    class_role_list = class_role_list[:len(class_role_list)-2] # trim last ', '
    getlist.add_field(name = 'Class Specific Roles', value=class_role_list, inline=False)
    getlist.set_footer(text='If you want a role added to the server @Caleb or suggest it in #suggestions')
    await ctx.message.author.send(embed=getlist)

async def list_my_roles(ctx, client, member):
    housing_roles, major_roles, graduation_year, pronoun, class_specific, special = '', '', '', '', '', ''
    class_specific_roles, special_roles = [], []
    
    for role in sorted(member.roles, key=lambda x: x.name):
        if role.id in PRONOUN_ROLE_IDS:
            pronoun = capitalize_all_words(role.name, '/') + '\n'
        if role.id in CLASS_ROLE_IDS:
            class_specific += role.name.upper() + '\n'
        name = capitalize_all_words(role.name, ' ')
        if role.id in HOUSING_ROLE_IDS:
            housing_roles += name + '\n'
        if role.id in MAJOR_ROLE_IDS:
            major_roles += name + '\n'
        if role.id in GRAD_YEAR_ROLE_IDS:
            graduation_year = name + '\n'
        if role.id in SPECIAL_ROLE_IDS:
            special += name + '\n'

    if special:
        mylist = discord.Embed(color=0xb5a2c8, description= '**' + special + '**')
    else:
        mylist = discord.Embed(color=0xb5a2c8)
    mylist.set_author(name = '' + member.name + '\'s roles', icon_url = member.avatar_url)

    if not housing_roles:
        mylist.add_field(
            name = 'Housing Roles', 
            value='Missing housing role, set your residential area role in #role-assignment', 
            inline=False)
    else:
        mylist.add_field(name = 'Housing Roles', value=housing_roles, inline=False)
    if not major_roles:
        mylist.add_field(
            name = 'Major Roles', 
            value='Missing major role, set at least one major/minor role in #role-assignment', 
            inline=False)
    else:
        mylist.add_field(name = 'Major Roles', value=major_roles, inline=False)
    if class_specific:
        mylist.add_field(name = 'Class Roles', value=class_specific, inline=False)
    if graduation_year:
        mylist.add_field(name = 'Graduation Year', value=graduation_year, inline=False)
    if pronoun:
        mylist.add_field(name = 'Pronoun', value=pronoun, inline=False)
    message = await ctx.channel.send(embed=mylist)    
    await del_convo(ctx.message, message, 30)

async def stats(ctx):
    contents = ctx.message.content[6:].strip().lower()
    if len(contents) == 0:
        message = await ctx.send(embed=discord.Embed(
            description="You must specify a valid role, for example: $stats Computer Science\n" \
                        "This message will auto-delete in 15 seconds",             
            color=discord.Color.red()))
        await del_convo(ctx.message, message, 15)
        return
    possible_roles = merge_dict([HOUSING_ROLE_IDS, MAJOR_ROLE_IDS, CLASS_ROLE_IDS, GRAD_YEAR_ROLE_IDS, PRONOUN_ROLE_IDS, SPECIAL_ROLE_IDS, PRONOUN_ROLE_IDS])
    found = False
    for role_id, role_names in possible_roles.items():
        for alias in role_names:
            if contents == alias: # valid role
                found = True
                role = get(ctx.guild.roles, id=role_id)
                break
    if not found:
        message = await ctx.send(embed=discord.Embed(
            description="Invalid role specified. You must specify a valid role, for example: $stats Computer Science\n" \
                        "This message will auto-delete in 15 seconds", 
            color=discord.Color.red()))
        await del_convo(ctx.message, message, 15)
        return
    message = await ctx.send(embed=discord.Embed(
        title=role.name + " Role Statistics", 
        description = "Count: " + str(len(role.members)) + "\n" \
                      "Percentage of Members: {:.3f}%".format((len(role.members)/ctx.message.guild.member_count)*100), 
        color=discord.Color.greyple()))
    await del_convo(ctx.message, message, 30)

async def block_multiple_restricted_roles(member, channel, ctx, id_dict, role_name, str_role_type):
    for roles in id_dict.values():
        if role_name in roles:
            message = await channel.send(embed=discord.Embed(
                description="I'm sorry, " + member.name + ", you already have a " + str_role_type +" role!\n" \
                            "Use the $remove [role] command to remove it in order to add a different one!\n" \
                            "This message will auto-delete in 15 seconds", 
                color=discord.Color.gold()))
            await del_convo(ctx.message, message, 15)
            return True
    return False

async def stem_add_role(ctx, member, client):
    channel = ctx.channel
    available_roles = merge_dict([HOUSING_ROLE_IDS, MAJOR_ROLE_IDS, CLASS_ROLE_IDS, GRAD_YEAR_ROLE_IDS, PRONOUN_ROLE_IDS])
    role_lower = ctx.message.content[5:].lower().strip().replace('[', '').replace(']', '')
    is_grad_role, is_pronoun_role = False, False

    #check if user already has a graduation role or a pronoun role
    for role in member.roles:
        for grad_years in GRAD_YEAR_ROLE_IDS.values():
            if role.name.lower() in grad_years:
                is_grad_role = True
        for pronouns in PRONOUN_ROLE_IDS.values():
            if role.name.lower() in pronouns:
                is_pronoun_role = True

    for role_names in available_roles.values():
        if role_lower in role_names:

            # check if member already has the requested role
            for member_role in member.roles:
                if member_role.name.lower() == role_names[0]:
                    message = await channel.send(embed=discord.Embed(
                        description="I'm sorry, " + member.name + ", you already have this role!\n" \
                                    "Use the `$remove " + member_role.name + "` command to remove it!\n" \
                                    "This message will auto-delete in 15 seconds",
                        color=discord.Color.gold()))
                    await del_convo(ctx.message, message, 15)
                    return

            # if the member doesnt already have the requested role get the role from the guild roles
            for role in ctx.message.guild.roles:
                if role.name.lower() == role_names[0]:
                    role_to_add = role
                    
            # make sure member isn't trying to add a second grad year role, they should only be allowed to have one
            if is_grad_role and await block_multiple_restricted_roles(member, 
                                                                      channel,
                                                                      ctx,
                                                                      GRAD_YEAR_ROLE_IDS,
                                                                      role_to_add.name.lower(),
                                                                      'graduation year'): return
            
            # make sure member isn't trying to add a second pronoun role
            if is_pronoun_role and await block_multiple_restricted_roles(member, 
                                                                         channel,
                                                                         ctx,
                                                                         PRONOUN_ROLE_IDS,
                                                                         role_to_add.name.lower(),
                                                                         'pronoun'): return 

            await member.add_roles(role_to_add)
            await check_major_housing_role(member, client, role_to_add, True)
            message = await channel.send(embed=discord.Embed(
                description="Added " + role_to_add.name + " to " + member.name + "\n" \
                            "Use the `$remove " + role_to_add.name + "` command to remove it!\n" \
                            "This message will auto-delete in 15 seconds", 
                color=discord.Color.green()))
            await del_convo(ctx.message, message, 15)
            return
    message = await channel.send(embed=discord.Embed(
        description="I'm sorry, " + member.name + ", there is no role with that name!\n" \
                    "Use the `$getlist` command to see the available roles\n" \
                    "This message will auto-delete in 15 seconds",
        color=discord.Color.red()))
    await del_convo(ctx.message, message, 15)


async def check_major_housing_role(member, client, role, is_add):
    member_has_hr = False
    member_has_m = False
    curr_roles = member.roles
    if is_add:
        curr_roles.append(role)
    else:
        if role in curr_roles:
            curr_roles.remove(role)
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

async def stem_remove_role(ctx, member, client):
    channel = ctx.channel
    removable_roles = merge_dict([HOUSING_ROLE_IDS, MAJOR_ROLE_IDS, CLASS_ROLE_IDS, GRAD_YEAR_ROLE_IDS, PRONOUN_ROLE_IDS])
    role_lower = ctx.message.content[8:].lower().strip().replace('[', '').replace(']', '') # requested role 
    rid = -1 # requested role id

    # get the requested role's role id
    for role_id, r_aliases in removable_roles.items():
        if role_lower in r_aliases:
            rid = role_id
            break

    # role doesn't exist or it's a role that shouldn't be removed
    if rid == -1:
        message = await channel.send(embed=discord.Embed(
                    description="I'm sorry, " + member.name + ", that is not a valid removable role.\n" \
                                "This message will auto-delete in 15 seconds", 
                    color=discord.Color.red()))
        await del_convo(ctx.message, message, 15)
        return

    # check to see if the user has the requested role
    for role in member.roles:
        if role.id == rid:
            await member.remove_roles(role)
            await check_major_housing_role(member, client, role, False)
            message = await channel.send(embed=discord.Embed(
                description="Removed " + role.name + " from " + member.name + "\n" \
                            "Use the `$get " + role.name + "` command to add it back!\n" \
                            "This message will auto-delete in 15 seconds",
                color=discord.Color.green()))
            await del_convo(ctx.message, message, 15)
            return
    message = await channel.send(embed=discord.Embed(
        description="I'm sorry, " + member.name + ", you don't have a role with that name\n" \
                    "This message will auto-delete in 15 seconds", 
        color=discord.Color.red()))
    await del_convo(ctx.message, message, 15)
