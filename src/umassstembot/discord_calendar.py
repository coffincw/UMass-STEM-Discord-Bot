import datetime
import discord
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.client import GoogleCredentials, OAuth2WebServerFlow

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'json-file.json')

    store = Storage(credential_path)
    credentials = store.get()
    # credentials_json = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
    # credentials = GoogleCredentials.from_json(cred_test)
    if not credentials or credentials.invalid:
        flow = OAuth2WebServerFlow(client_id=GOOGLE_CLIENT_ID,
                                  client_secret=GOOGLE_CLIENT_SECRET,
                                  scope='https://www.googleapis.com/auth/calendar',
                                  redirect_uris=["urn:ietf:wg:oauth:2.0:oob","http://localhost"])
        flow.user_agent = 'calendar-stff'
        credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials 

async def get_events(ctx):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    creds = get_credentials()
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    # if os.path.exists('token.pickle'):
    #     with open('token.pickle', 'rb') as token:
    #         creds = pickle.load(token)
    # print(creds)
    # # If there are no (valid) credentials available, let the user log in.
    # if not creds or not creds.valid:
    #     if creds and creds.expired and creds.refresh_token:
    #         creds.refresh(Request())
    #     else:
    #         flow = InstalledAppFlow.from_client_secrets_file(
    #             'credentials.json', SCOPES)
    #         creds = flow.run_local_server(port=0)
    #     # Save the credentials for the next run
    #     with open('token.pickle', 'wb') as token:
    #         pickle.dump(creds, token)
    
    print(creds)
    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    # print(service.calendarList().list(pageToken=None).execute())
    events_result = service.events().list(calendarId='hca1n2eds4ohvrrg117jkodmk8@group.calendar.google.com', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    #print(events_result)
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

    await ctx.send(embed=discord.Embed(description="yay", color=discord.Color.green()))