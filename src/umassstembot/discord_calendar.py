import datetime
import discord
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

WEEKDAYS = ("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")
MONTHS = ("January", "February")

async def get_credentials(ctx, client):
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'json-file.json')

    store = Storage(credential_path)
    credentials = store.get()
    credentials = None

    if not credentials or credentials.invalid:
        flow = OAuth2WebServerFlow(client_id=GOOGLE_CLIENT_ID,
                                  client_secret=GOOGLE_CLIENT_SECRET,
                                  scope='https://www.googleapis.com/auth/calendar',
                                  redirect_uri='http://id.heroku.com/oauth/authorize',
                                  prompt='consent')
        flow.user_agent = 'calendar-stff'
        authorize_url = flow.step1_get_authorize_url()
        await ctx.send(authorize_url)
        code = await client.wait_for('message')
        print(code.content)
        credentials = flow.step2_exchange(code.content)
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