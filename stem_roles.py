import discord

HOUSING_ROLE_IDS = {'501529720932925441': ('alumni', 'alum', 'alumn'),
                    '444332276483096586': ('sylvan', 'syl', 'brown', 'cashin', 'mcnamara'),
                    '444332646307201034': ('ohill', 'orchard hill', 'o hill', 'grayson', 'field', 'dickinson', 'webster'),
                    '444332880894754818': ('central','baker', 'van meter', 'brett', 'brooks', 'butterfield', 'chadbourne', 'gorman', 'greenough', 'wheeler'), 
                    '444332735838814210': ('southwest', 'sw', 'swest', 'cance', 'coolidge', 'crampton', 'emerson', 'james', 'john adams', 'ja', 'jqa', 'john quincy adams', 'kennedy', 'mackimmie', 'melville', 'moore', 'patterson', 'pierpont', 'prince', 'thoreau', 'washington'),
                    '444332948322517003': ('northeast', 'ne', 'crabtree', 'dwight', 'hamlin', 'johnson', 'knowlton', 'leach', 'lewis', 'mary lyon', 'thatcher'),
                    '444588763427897344': ('north apts', 'north apartments', 'north apartment'), 
                    '444333125670010890': ('honors college', 'birch', 'elm', 'linden', 'maple', 'oak', 'sycamore'),
                    '405025553448566795': ('off-campus', 'off campus', 'offcampus', 'commute', 'commuter'),
                    '524016335299280908': ('prospective student', 'hs', 'high school', 'accepted', 'accepted student')
}

MAJOR_ROLE_IDS = {'442786317273792523': ('electrical engineering', 'ee', 'electrical-engineering'),
                  '506504010585604132': ('computer engineering', 'ce', 'comp-engineering', 'computer-engineering'),
                  '504715524152754199': ('chemical engineering', 'cheme'),
                  '506504177242079241': ('biomedical engineering', 'be', 'bio-engineering'),
                  '442806923025186817': ('environmental engineering', 'environmental-engineering'),
                  '506211361945288735': ('civil engineering', 'civil-engineering'),
                  '501524792436981791': ('industrial and mechanical engineering', 'ime', 'industrial engineering', 'me', 'ie', 'mechanical engineering', 'industrial mechanical engineering'),
                  '439552642415460353': ('ece', 'electrical and computer engineering', 'ec engineering'),
                  '387619060633829377': ('computer science', 'cs', 'compsci', 'comp-sci'),
                  '442784019369951252': ('environmental science', 'es'),
                  '442785279493799966': ('math', 'mathematics'),
                  '387670593987805184': ('economics', 'econ'),
                  '405032140040830998': ('informatics', 'info'),
                  '506223375056633856': ('information technology', 'information tech', 'it'),
                  '405035782269829121': ('political science', 'polisci', 'poli-sci'),
                  '442784136457879567': ('biology', 'bio'),
                  '442784769273626626': ('plant science',), 
                  '442822241135230978': ('geology', 'geo'), 
                  '506253630714806272': ('food science',),
                  '443558312794128407': ('history',),
                  '447463828398145537': ('physics',),
                  '536247576496701440': ('bdic', 'bachelors degree with individual concentration'),
                  '405932216808505355': ('communication', 'communications', 'comm', 'com'),
                  '490210619270889486': ('nutrition',),
                  '501525484257935360': ('biochemistry', 'biochem'),
                  '501608246579167233': ('microbiology', 'microbio'),
                  '502556060171894785': ('animal science', 'animal'),
                  '502624207390244864': ('animation',),
                  '507634130842812441': ('business', 'isenberg'),
                  '509005908072726533': ('accounting', 'account'),
                  '517414427390378041': ('linguistics', 'ling'),
                  '551464859301314572': ('comparative literature', 'comp lit', 'comp-lit'),
                  '522165967481208833': ('chinese',),
                  '522166045939597335': ('japanese',),
                  '524039481486213151': ('psychology', 'psych'),
                  '543109471136645161': ('public health', 'pub health', 'pub hlth'),
                  '524777786972307477': ('education', 'educ'),
                  '539870761754820628': ('english',),
                  '387619488880787457': ('cics exploratory', 'cs exploratory', 'cs explo', 'exploratory computer science', 'computer science exploratory', 'exporatory cs', 'exploratory'), 
                  '506211413564325919': ('engineering undecided', 'engineering-undecided', 'undecided engineering', 'engineering'),
                  '501908170654875648': ('undecided',)
}

CLASS_ROLE_IDS = {'539872888124211200': ('cs 121', 'cs121', '121'),
                  '539872925902438400': ('cs 186', 'cs186', '186'),
                  '539872976523362305': ('cs 187', 'cs187', '187'),
                  '505504445728161812': ('cs 220', 'cs220', '220'),
                  '505504337590484992': ('cs 230', 'cs230', '230'),
                  '506226744001560596': ('cs 240', 'cs240', '240'),
                  '505504252110831629': ('cs 250', 'cs250', '250'),
                  '550746699468111872': ('cs 305', 'cs305', '305'),
                  '532274256063627296': ('cs 311', 'cs311', '311'),
                  '543883289296109578': ('cs 320', 'cs320', '320'),
                  '543883169385021450': ('cs 326', 'cs326', '326'),
                  '540257612332269588': ('cs 377', 'cs377', '377'),
                  '539871233622278144': ('cs 383', 'cs383', '383'),
                  '539871350731309116': ('math 131', 'math131', '131', 'calc 1'),
                  '539871571028738078': ('math 132', 'math132', '132', 'calc 2'),
                  '539871622627196939': ('math 233', 'math233', '233', 'calc 3'),
                  '539871699085295626': ('math 235', 'math235', '235', 'linear algebra'),
                  '544265492081410048': ('math 300', 'math300', '300'),
                  '544265410309259265': ('math 331', 'math331', '331', 'calc 4'),
                  '544268317725294593': ('math 411', 'math411', '411'),
                  '550746745613582361': ('math 425', 'math425', '425'),
                  '544265554492653569': ('math 551', 'math551', '551'),
                  '543882513131765791': ('math 523h', 'math523h', '523h'),
                  '543882645738619095': ('math 534h', 'math534h', '534h'),
                  '539871808883785748': ('stats 515', 'stat 515', 'stats515', 'stat515' '515'),
                  '543882390888513546': ('stats 516', 'stat 516', 'stat516', 'stats516', '516'),
                  '543883063923310602': ('micro 160', 'microbio 160', 'micro160', 'microbio160')
}

def merge_dict(w, x, y): # merges dictionaries w, x, y together
    z = x.copy()
    z.update(y)
    z.update(w)
    return z

async def list_roles(ctx, client):
    getlist = discord.Embed(color=discord.Color.blue())
    getlist.set_author(name='Roles | Use $get [role] to add a role', icon_url='https://cdn.discordapp.com/attachments/501594682820788224/558396074868342785/UMass_Stem_discord_logo.png')
    housing_role_list = ''
    for role in HOUSING_ROLE_IDS.values():
        housing_role_list += role[0].capitalize() + '\n'
    getlist.add_field(name = 'Housing Roles', value=housing_role_list, inline=False)
    major_role_list = ''
    for role in MAJOR_ROLE_IDS.values():
        major_role_list += role[0].capitalize() + '\n'
    getlist.add_field(name = 'Major Roles', value=major_role_list, inline=False)
    class_role_list = ''
    for role in CLASS_ROLE_IDS.values():
        if class_role_list == '':
            class_role_list += '**Computer Science**\n'
        if role[0].startswith('cs'):
            class_role_list += role[0][0].capitalize() 
            class_role_list += role[0][1:].capitalize() + ', '
            continue
        if role[0].endswith('131'):
            class_role_list = class_role_list[:len(class_role_list)-2]
            class_role_list += '\n**Mathematics**\n'
        if role[0].startswith('math') or role[0].startswith('stats'):
            class_role_list += role[0].capitalize() + ', '
            continue
        class_role_list = class_role_list[:len(class_role_list)-2]
        class_role_list += '\n**Other**\n'
        class_role_list += role[0].capitalize()
    getlist.add_field(name = 'Class Specific Roles', value=class_role_list, inline=False)
    getlist.set_footer(text='If you want a role added to the server @Caleb or suggest it in #suggestions')
    await client.send_message(ctx.message.channel, embed=getlist) 

async def stem_add_role(requested_role, member, client):
    available_roles = merge_dict(HOUSING_ROLE_IDS, MAJOR_ROLE_IDS, CLASS_ROLE_IDS)
    role_lower = requested_role.message.content[5:].lower()
    for role_names in available_roles.values():
        for alias in role_names:
            if role_lower == alias: # valid role
                # check if member already has the requested role
                for member_role in member.roles:
                    if member_role.name.lower() == role_names[0]:
                        await client.send_message(requested_role.message.channel, embed=discord.Embed(description="I'm sorry, " + member.name + ", you already have this role!\nUse the $remove [role] command to remove it!", color=discord.Color.gold())) 
                        return
                # if the member doesnt already have the requested role
                for role in requested_role.message.server.roles:
                    if role.name.lower() == role_names[0]:
                        role_to_add = role
                await client.add_roles(member, role_to_add)
                await check_major_housing_role(member, client)
                await client.send_message(requested_role.message.channel, embed=discord.Embed(description="Added " + role_to_add.name + " to " + member.name + "\nUse the $remove [role] command to remove it!", color=discord.Color.green())) 
                return
    await client.send_message(requested_role.message.channel, embed=discord.Embed(description="I'm sorry, " + member.name + ", there is no role with that name!\nUse the $getlist command to see the available roles", color=discord.Color.red()))

async def check_major_housing_role(member, client):
    member_has_hr = False
    member_has_m = False
    for role in member.roles:
        if role.id in HOUSING_ROLE_IDS:
            member_has_hr = True
        if role.id in MAJOR_ROLE_IDS:
            member_has_m = True
    for role in member.server.roles:
        if role.name.lower() == 'missing housing or major role':
            mhom = role
    if mhom in member.roles: # check if the member has the missing housing or major role             
        if member_has_hr and member_has_m:
            await client.remove_roles(member, mhom) #removes missing housing or major role
    else: # if not then add it to them if they need it
        if not member_has_hr or not member_has_m:  
            await client.add_roles(member, mhom) #adds missing housing or major role if they dont have the roles

async def stem_remove_role(requested_role, member, client):
    removable_roles = merge_dict(HOUSING_ROLE_IDS, MAJOR_ROLE_IDS, CLASS_ROLE_IDS)
    role_lower = requested_role.message.content[8:].lower()
    for role in member.roles:
        if role.id in removable_roles.keys() and role_lower in removable_roles[role.id]:
            for housing_major_role in removable_roles.values():
                for alias in housing_major_role:
                    if role_lower == alias:
                        await client.remove_roles(member, role)
                        await check_major_housing_role(member, client)
                        await client.send_message(requested_role.message.channel, embed=discord.Embed(description="Removed " + role.name + " from " + member.name, color=discord.Color.green()))
                        return
            await client.send_message(requested_role.message.channel, embed=discord.Embed(description="I'm sorry, " + member.name + ", you can't remove that role", color=discord.Color.red()))
            return
    await client.send_message(requested_role.message.channel, embed=discord.Embed(description="I'm sorry, " + member.name + ", you don't have a role with that name", color=discord.Color.red()))

            