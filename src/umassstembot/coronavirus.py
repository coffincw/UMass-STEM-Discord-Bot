from bs4 import BeautifulSoup
import dateutil.parser
import discord
import requests
import os

FINNHUB_CORONA_TOKEN = os.environ.get('FINNHUB_API_TOKEN_5')

us_areas = {'AL': ['Alabama', '4903185'],
            'AK': ['Alaska', '731545'],
            'AZ': ['Arizona', '7278717'],
            'AR': ['Arkansas', '3017804'],
            'CA': ['California', '39512223'],
            'CO': ['Colorado', '5758736'],
            'CT': ['Connecticut', '3565278'],
            'DE': ['Delaware', '973764'],
            'FL': ['Florida', '21477737'],
            'GA': ['Georgia', '10617423'],
            'HI': ['Hawaii', '1415872'],
            'ID': ['Idaho', '1787065'],
            'IL': ['Illinois', '12671821'],
            'IN': ['Indiana', '6732219'],
            'IA': ['Iowa', '3155070'],
            'KS': ['Kansas', '2913314'],
            'KY': ['Kentucky', '4467673'],
            'LA': ['Louisiana', '4648794'],
            'ME': ['Maine', '1344212'],
            'MD': ['Maryland', '6045680'],
            'MA': ['Massachusetts', '6892503'],
            'MI': ['Michigan', '9986857'],
            'MN': ['Minnesota', '5639632'],
            'MS': ['Mississippi', '2976149'],
            'MO': ['Missouri', '6137428'],
            'MT': ['Montana', '1068778'],
            'NE': ['Nebraska', '1934408'],
            'NV': ['Nevada', '3080156'],
            'NH': ['New Hampshire', '1359711'],
            'NJ': ['New Jersey', '8882190'],
            'NM': ['New Mexico', '2096829'],
            'NY': ['New York', '19453561'],
            'NC': ['North Carolina', '10488084'],
            'ND': ['North Dakota', '762062'],
            'OH': ['Ohio', '11689100'],
            'OK': ['Oklahoma', '3956971'],
            'OR': ['Oregon', '4217737'],
            'PA': ['Pennsylvania', '12801989'],
            'RI': ['Rhode Island', '1059361'],
            'SC': ['South Carolina', '5148714'],
            'SD': ['South Dakota', '884659'],
            'TN': ['Tennessee', '6829174'],
            'TX': ['Texas', '28995881'],
            'UT': ['Utah', '3205958'],
            'VT': ['Vermont', '623989'],
            'VA': ['Virginia', '8535519'],
            'WA': ['Washington', '7614893'],
            'WV': ['West Virginia', '1792147'],
            'WI': ['Wisconsin', '5822434'],
            'WY': ['Wyoming', '578759'],
            'DC': ['District of Columbia', '705749']
            }

UMASS_CASE_EPOCH = dateutil.parser.parse("2020-08-14 00:00:00")


async def coronavirus(ctx, sort_by_percentage):
    """Generate coronavirus statistics

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
        - sort_by_percentage: true when we want to sort by percentage infected, false when we want to sort by # of cases
        - args: optional, if state is passed in return the states cases and deaths, if nothing then return the top 15
    """
    if sort_by_percentage:
        argument = ctx.message.content[7:].strip().strip('\"') # after '$covidp' remove spaces
    else:
        argument = ctx.message.content[6:].strip().strip('\"') # after '$covid' remove spaces
    try:
        data = requests.get('https://finnhub.io/api/v1/covid19/us?&token=' + FINNHUB_CORONA_TOKEN).json()
    except:
        print(requests.get('https://finnhub.io/api/v1/covid19/us?&token=' + FINNHUB_CORONA_TOKEN))
        await ctx.channel.send(embed=discord.Embed(
            description="API limit reached, please wait before running the command again.", 
            color=discord.Color.red()))
        return
    only_states_data = [block for block in data if block['state'] in get_states()]
    if len(argument) < 1:
        embed = discord.Embed(title='Coronavirus Statistics', color=discord.Color.teal())
        i = 1
        case_count = 0
        pop_count = 0
        death_count = 0
        for state in sorted(only_states_data, 
                            key=lambda state: state['case'] if not sort_by_percentage else (state['case']/get_pop(state['state'].strip())), 
                            reverse=True): # iterate through the state blocks sorted by case number
            
            case_count += state['case']
            death_count += state['death']
            pop_count += get_pop(state['state'].strip())
            if i < 16:
                state_name, cases_output, deaths_output = build_top_corona_output(state)
                embed.add_field(
                    name = str(i) + '. ' + state_name + '\n', 
                    value = 'Cases: ' + cases_output + 'Deaths: ' + deaths_output, 
                    inline=True)
            i += 1

        embed.description = '-------= U.S Totals =-------\n' \
                            'Cases: {:,d} '.format(case_count) + '(' + str(round((case_count/pop_count) * 100, 4)) + '%)' + '\n' \
                            'Deaths: {:,d} '.format(death_count) + '(' + str(round((death_count/pop_count) * 100, 4)) + '%)'
        await ctx.send(embed=embed)

    else:
        try:
            state = us_areas[argument.upper()][0]
            population = int(us_areas[argument.upper()][1])
        except:
            state = capitalize_all_words(argument)
            if get_abbrev(state) == '':
                await ctx.channel.send(embed=discord.Embed(
                    description="Invalid state, make sure you use the full name not the abbreviation", 
                    color=discord.Color.red()))
                return
            population = get_pop(state)
        description = ''
        for block in only_states_data:
            if str(block['state']).strip() == state:
                pop_percentage = round((block['case']/population) * 100, 4)
                description = 'Cases: ' + '{:,d}'.format(block['case'])
                description += '\nInfected Percentage: ' + str(pop_percentage) + '%'
                description += '\nDeaths: ' + '{:,d}'.format(block['death'])
                description += '\nFatality Rate: ' + '{:,.2f}%'.format((block['death']/block['case']) * 100)
                break
        embed = discord.Embed(
            title=state + ' Coronavirus Statistics', 
            description=description, 
            color=discord.Color.teal())
        await ctx.send(embed=embed)

def get_states():
    """Returns a list of U.S states
    """
    states = []
    for abbrev, value in us_areas.items():
        states.append(value[0])
    return states

def get_abbrev(state):
    """Returns the abbreviation of the passed in state

       Args:
        - state: state in which to get the abbreviation
    """
    abbrev_list = [key for key, value in us_areas.items() if state in value]

    return abbrev_list[0] if len(abbrev_list) > 0 else ''

def get_pop(state):
    """Returns the population of the passed in state

       Args:
        - state: state in which to get the population
    """
    abbrev = get_abbrev(state)
    return int(us_areas[abbrev][1]) if abbrev != '' else -1


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

def build_top_corona_output(state):
    """Returns the outputs needed for the top coronavirus embed

       Args:
        - state: state in which to get the statistics
    """
    pop = get_pop(state['state'].strip())
    
    cases_perc = state['case']/pop * 100
    fatal_perc = state['death']/state['case'] * 100 # calculate fatality rate

    cases_output = '{:,d}'.format(state['case']) + ' ({:,.2f}%)'.format(cases_perc) + '\n' # format integers with commas
    deaths_output = '{:,d}'.format(state['death']) + ' ({:,.2f}%)'.format(fatal_perc)
    
    return state['state'], cases_output, deaths_output

async def umass_coronavirus(ctx):
    """Generate UMass-specific coronavirus statistics

       Args:
        - ctx: context that the command occured use this to access the message and other attributes
    """
    try:
        data = requests.get('https://www.umass.edu/coronavirus/confirmed-cases-covid-19-umass-amherst').text
    except:
        print(requests.get('https://www.umass.edu/coronavirus/confirmed-cases-covid-19-umass-amherst'))
        await ctx.channel.send(embed=discord.Embed(
            description="Could not access reporting page, please wait before running the command again.", 
            color=discord.Color.red()))
        return

    total_cases = 0
    most_recent_report = None
    most_recent_count  = None

    soup = BeautifulSoup(data, 'html.parser')
    for accordion in soup.select(".field-group-accordion-wrapper"):
        date = accordion.select(".field--name-node-title")[0].get_text().strip()
        date = dateutil.parser.parse(date)

        case_count = accordion.select(".field--name-field__of-reported-cases")[0] \
                              .select(".field__item")[0] \
                              .get_text()
        case_count = int(case_count)

        if date >= UMASS_CASE_EPOCH:
            if most_recent_report is None or date > most_recent_report:
                most_recent_report = date
                most_recent_count = case_count

            total_cases += case_count

    embed = discord.Embed(title='UMass Coronavirus Statistics', color=discord.Color.teal())
    embed.description = "{} cases since {}".format(total_cases, UMASS_CASE_EPOCH.strftime("%Y-%m-%d")) + \
                        "\n" + \
                        "Most recent report: {} case(s) on {}.".format(most_recent_count, most_recent_report.strftime("%Y-%m-%d"))
    await ctx.send(embed=embed)
