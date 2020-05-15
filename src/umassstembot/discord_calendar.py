import datetime
import discord
import requests
import pickle
import bs4
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
    creds = None
    creds = await get_credentials(ctx, client)
   
    service = build('calendar', 'v3', credentials=creds)

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
        
        #print(event)
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
            soup = bs4.BeautifulSoup(event['description'])
            aTags = soup.find_all("a")
            urls = [tag['href'] for tag in aTags if 'href' in tag.attrs]
            te_link = '[Tournament Event Link](' + urls[0] + ')' # tournament link needs to be the first url
            event_desc += '\n' + te_link
        calendar_output_embed.add_field(name=event['summary'], value= event_desc, inline=False)

    await ctx.send(embed=calendar_output_embed)