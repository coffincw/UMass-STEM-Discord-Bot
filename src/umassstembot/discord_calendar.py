import datetime
from dateutil.parser import parse as dtparse
import discord
import requests
import pickle
import bs4
import time
import re
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import google.oauth2.credentials
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.client import GoogleCredentials, OAuth2WebServerFlow

# If modifying these scopes, delete the file token.pickle.
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
GOOGLE_REFRESH_TOKEN = os.environ.get('GOOGLE_REFRESH_TOKEN')

CREDS = None

WEEKDAYS = ("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")
MONTHS = ("January", "February")

def refreshToken(client_id, client_secret, refresh_token):
        params = {
                "grant_type": "refresh_token",
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token
        }

        authorization_url = "https://www.googleapis.com/oauth2/v4/token"

        r = requests.post(authorization_url, data=params)

        if r.ok:
                return r.json()['access_token']
        else:
                return None

async def get_credentials(ctx, client):
    credentials = None
    # with open('refresh.token', 'r') as f:
    #     refresh_token = f.readline()
    access_token = refreshToken(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN)
    credentials = google.oauth2.credentials.Credentials(access_token)

    

    if not credentials or not credentials.valid:
        flow = OAuth2WebServerFlow(client_id=GOOGLE_CLIENT_ID,
                                  client_secret=GOOGLE_CLIENT_SECRET,
                                  scope='https://www.googleapis.com/auth/calendar',
                                  redirect_uri='http://id.heroku.com/oauth/authorize',
                                  prompt='consent')
        flow.user_agent = 'calendar-stff'
        authorize_url = flow.step1_get_authorize_url()
        # change this to give an error message and dm caleb instead
        await ctx.send(authorize_url)
        message = await client.wait_for('message')
        code = message.content
        credentials = flow.step2_exchange(code)
        # with open('refresh.token', 'w+') as f:
        #     f.write(credentials.refresh_token)
        await ctx.send(credentials.refresh_token)
        #credentials = tools.run_flow(flow, store)
        # print('Storing credentials to ' + credential_path)
    return credentials 

def convert_time(str_time):
    date_time = str_time.split('T')
    mil_time = date_time[1].split('-')[0]
    time = datetime.datetime.strptime(mil_time, '%H:%M:%S').strftime('%I:%M:%S %p')
    return date_time[0], time

async def get_events(ctx, client):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    global CREDS
    if CREDS is None:
        CREDS = await get_credentials(ctx, client)
   
    service = build('calendar', 'v3', credentials=CREDS)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    # print(service.calendarList().list(pageToken=None).execute())
    events_result = service.events().list(calendarId='hca1n2eds4ohvrrg117jkodmk8@group.calendar.google.com', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    #print(events)
    
    if not events:
        calendar_output_embed = discord.Embed(title=events_result['summary'], description='No upcoming events!', color=discord.Color.red())
    else:
        calendar_output_embed = discord.Embed(title=events[0]['organizer'].get('displayName'), color=discord.Color.dark_teal())
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        time = convert_time(start)
        date = time[0].split('-')
        date_time_date= datetime.date(int(date[0]), int(date[1]), int(date[2]))
        month = date_time_date.strftime('%b')
        day = date_time_date.weekday()
        day_str = WEEKDAYS[day]
        title = ''
        calendar_event_link = '[Calendar Event Link](' + event['htmlLink'] + ')'
        event_desc = time[1] + ' ' + day_str + ' ' + month + ' ' + date[2] + ' ' + date[0] + '\n' + calendar_event_link
        if 'description' in event and '<a href=' in event['description'].strip():
            # print(event['description'])
            soup = bs4.BeautifulSoup(event['description'])
            aTags = soup.find_all("a")
            urls = [tag['href'] for tag in aTags if 'href' in tag.attrs]
            te_link = '[Tournament Event Link](' + urls[0] + ')' # tournament link needs to be the first url
            event_desc += '\n' + te_link
        calendar_output_embed.add_field(name=event['summary'], value= event_desc, inline=False)

    await ctx.send(embed=calendar_output_embed)

async def set_time(ctx, starttime_arg):
    time_zone_str = '-05:00' if time.localtime().tm_isdst == 0 else '-04:00'
    if not (starttime_arg.endswith('pm') or starttime_arg.endswith('am')):
        await ctx.send(embed=discord.Embed(description="Invalid time format. Please end with 'am' or 'pm'! ex. 12:00 pm", color=discord.Color.red()))
        return ''

    time_value = starttime_arg[:-2].rstrip() # trim off 'pm' or 'am'
    hours_min = time_value.split(':')
    if len(hours_min) != 2:
        await ctx.send(embed=discord.Embed(description="Invalid time format. Please use ex. 12:00 pm", color=discord.Color.red()))
        return ''
    hours = int(hours_min[0])
    minutes = int(hours_min[1])

    if starttime_arg.endswith('pm'):
        hours += 12
        
    
    if hours > 23 or minutes > 59 or hours < 0  or minutes < 0:
        await ctx.send(embed=discord.Embed(description="Invalid time!", color=discord.Color.red()))
        return ''

    if hours < 10:
        hours_str = '0' + str(hours)
    else:
        hours_str = str(hours)

    if minutes < 10:
        minutes_str = '0' + str(minutes)
    else:
        minutes_str = str(minutes)

    return hours_str + ':' + minutes_str + ':00' + time_zone_str

async def check_and_format_date(ctx, date_arg):

    if re.match(r"\d{4}-\b(0?[1-9]|[1][0-2])\b-\b(0?[1-9]|[12][0-9]|3[01])\b", date_arg): #1999-01-25 (year- month - day)

        date_arr = date_arg.split('-')
        try:
            temp_date = datetime.datetime(int(date_arr[0]), int(date_arr[1]), int(date_arr[2]))
        except ValueError:
            await ctx.send(embed=discord.Embed(description="Invalid date! Please use a real date.", color=discord.Color.red()))
            return ''
        if len(date_arr[1]) < 2:
            print('month less than 2 digits')
            date_arg = date_arg[:5] + '0' + date_arg[5:]
        print('check day')
        print(date_arr[2])
        if len(date_arr[2]) < 2:
            print('day less than 2 digits')
            date_arg = date_arg[:8] + '0' + date_arg[8:]
    else:
        await ctx.send(embed=discord.Embed(description="Invalid date! Please use a date in this format: year-month-day.\nex. 2020-5-20", color=discord.Color.red()))
        return ''
    return date_arg

async def set_end_time(ctx, duration, start_time):
    start_datetime = dtparse(start_time)
    end_datetime = start_datetime + datetime.timedelta(minutes=int(duration))
    end = end_datetime.strftime("%Y-%m-%dT%H:%M:%S")
    time_zone_str = '-05:00' if time.localtime().tm_isdst == 0 else '-04:00'
    return end + time_zone_str

async def add_events(ctx, client, args):
    global CREDS
    if CREDS is None:
        CREDS = await get_credentials(ctx, client)

    service = build('calendar', 'v3', credentials=CREDS)
    date_arg = args[0].strip()
    starttime_arg = args[1].strip().lower()
    duration = args[2].strip()
    if int(duration) < 15 or int(duration) > 1440:
        await ctx.send(embed=discord.Embed(description="Invalid duration, please input a duration (in minutes) between 15 and 1440.", color=discord.Color.red()))
        return
    summary = args[3].strip()
    
    if len(args) > 4:
        link = args[4].strip()
    
        regex = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
            r'localhost|' #localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if not re.match(regex, link):
            await ctx.send(embed=discord.Embed(description="Invalid value used for link parameter.", color=discord.Color.red()))
            return
    else:
        link = ''
    print(date_arg)
    date_str = await check_and_format_date(ctx, date_arg)
    if len(date_str) < 1:
        return
    start_time = await set_time(ctx, starttime_arg)
    if len(start_time) < 1:
        return
    end_time = await set_end_time(ctx, duration, date_str + 'T' + start_time)
    print(end_time)
    

    # need to parse date and create end time



    # to make all day events use 'date' field instead of 'dateTime' field and just use date (ex. 2020-05-20)
    new_event = {
        'summary': summary,
        'description': '<a href=\"' + link + '\">' + link + '</a>&nbsp;&nbsp;',
        'start': {
            'dateTime': date_str + 'T' + start_time,
            'timeZone': 'America/New_York'
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'America/New_York'
        }

    }
    print(new_event)
    # event = service.events().insert(calendarId='hca1n2eds4ohvrrg117jkodmk8@group.calendar.google.com', body=event).execute()