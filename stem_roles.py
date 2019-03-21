import discord



HOUSING_ROLE_IDS = {'501529720932925441': ('alumni', 'alum', 'alumn'),
                    '444332276483096586': ('sylvan', 'syl'),
                    '444332646307201034': ('ohill', 'orchard hill', 'o hill'),
                    '444332880894754818': ('central',), 
                    '444332735838814210': ('southwest', 'sw', 'swest'),
                    '444332948322517003': ('northeast', 'ne'),
                    '444588763427897344': ('north apts', 'north apartments', 'north apartment'), 
                    '444333125670010890': ('honors college',),
                    '405025553448566795': ('off-campus', 'off campus', 'offcampus', 'commute', 'commuter'),
                    '524016335299280908': ('prospective student', 'hs', 'high school')
}

MAJOR_ROLE_IDS = {'442786317273792523': ('electrical engineering', 'ee', 'electrical-engineering'),
                  '506504010585604132': ('computer engineering', 'ce', 'comp-engineering', 'computer-engineering'),
                  '504715524152754199': ('biomedical engineering', 'be', 'bio-engineering'),
                  '506504177242079241': ('environmental engineering', 'environmental-engineering'),
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
                  '405932216808505355': ('communications', 'communication', 'comm', 'com'),
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
                  '541744140191268894': ('women, gender, and sexuality studies'),
                  '524777786972307477': ('education', 'educ'),
                  '539870761754820628': ('english',),
                  '387619488880787457': ('cics exploratory', 'cs exploratory', 'cs explo', 'exploratory computer science', 'computer science exploratory', 'exporatory cs', 'exploratory'), 
                  '506211413564325919': ('engineering undecided', 'engineering-undecided', 'undecided engineering', 'engineering'),
                  '501908170654875648': ('undecided',)
}

def merge_dict(x, y):
    z = x.copy()
    z.update(y)
    return z

async def stem_add_role(requested_role, member, client):
    available_roles = merge_dict(HOUSING_ROLE_IDS, MAJOR_ROLE_IDS)
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
        print("test")
        if not member_has_hr or not member_has_m:  
            await client.add_roles(member, mhom) #adds missing housing or major role if they dont have the roles

async def stem_remove_role(requested_role, member, client):
    removable_roles = merge_dict(HOUSING_ROLE_IDS, MAJOR_ROLE_IDS)
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

            