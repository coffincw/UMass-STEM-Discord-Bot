import discord
import requests
import os

FINNHUB_CORONA_TOKEN = os.environ.get('FINNHUB_API_TOKEN_5')

async def coronavirus(ctx):
    """Generate coronavirus statistics

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
        - args: optional, if state is passed in return the states cases and deaths, if nothing then return the top 15
    """
    argument = ctx.message.content[6:].strip() # after '$covid' remove spaces
    data = requests.get('https://finnhub.io/api/v1/covid19/us?&token=' + FINNHUB_CORONA_TOKEN).json()
    if len(argument) < 1:
        embed = discord.Embed(title='Coronavirus Statistics', color=discord.Color.teal())
        i = 1
        for state in sorted(data, key=lambda state: state['case'], reverse=True): # iterate through the state blocks sorted by case number
            fatal_perc = state['death']/state['case'] * 100 # calculate fatality rate
            cases_output = '{:,d}'.format(state['case']) + '\n' # format integers with commas
            deaths_output = '{:,d}'.format(state['death']) + ' ({:,.2f}%)'.format(fatal_perc)
            embed.add_field(name = str(i) + '. ' + state['state'] + '\n', value = 'Cases: ' + cases_output + 'Deaths: ' + deaths_output, inline=True)
            i += 1
            if i > 15:
                break
        await ctx.send(embed=embed)

    else:
        state = capitalize_all_words(argument)
        found = False
        description = ''
        for block in data:
            if str(block['state']).strip() == state:
                found = True
                description = 'Cases: ' + '{:,d}'.format(block['case'])
                description += '\nDeaths: ' + '{:,d}'.format(block['death'])
                description += '\nFatality Rate: ' + '{:,.2f}%'.format((block['death']/block['case']) * 100)
                break
        
        if not found:
            await ctx.channel.send(embed=discord.Embed(description="Invalid state, make sure you use the full name not the abbreviation", color=discord.Color.red()))
            return
        else:
            embed = discord.Embed(title=state + ' Coronavirus Statistics', description=description, color=discord.Color.teal())
        await ctx.send(embed=embed)

def capitalize_all_words(str):
    """Capitalizes all words in the string

       Args:
        - str: passed in string to be capitalized
    """
    string_list = str.split()
    output = ''
    for string in string_list:
        output += string.capitalize() + ' '
    output = output[:-1]
    return output