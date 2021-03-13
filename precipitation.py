# For OpenWeatherMap (OWM)
import requests
import json

# For Google Calendar
from datetime import datetime, timedelta
import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Misc
from dotenv import load_dotenv
load_dotenv()

# OWM API, Location, and Data
api_key = os.getenv('api_key')
lat = os.getenv('lat')
lon = os.getenv('lon')
part = 'current,minutely,hourly'

url = f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude={part}&appid={api_key}&units=metric'
response = requests.get(url)
data = json.loads(response.text)

# Google Calendar Access
SCOPES = ['https://www.googleapis.com/auth/calendar']

creds = None
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('calendar', 'v3', credentials=creds)
# Get Google Calendar ID
# Replace with 'primary' if adding to default calendar
cal_id = os.getenv('cal_id')

# Check forecast and add weather events
forecast = data['daily']
for date in forecast:
  # date['dt'] is in Unix, convert to UTC:
  timestamp = datetime.fromtimestamp(date['dt'])
  # Convert to ISO, keep only the date
  day = timestamp.isoformat()[:-9]
  print(f"\nOWM Date: {day}")
  # Add 1 day to create an end day for event:
  end_day = timestamp + timedelta(days = +1)
  # Convert to ISO, keep only the date
  end_day = end_day.isoformat()[:-9]

  # Weather Info:
  for weather_type in date['weather']:
    weather_descript = (weather_type['description'].title())

    # If precipitation,
    if 'Rain' in weather_descript or 'Snow' in weather_descript:
      print('Precipitation found!')
      if 'Rain' in weather_descript and 'Snow' in weather_descript:
        emoji = '\U0001F328'
        precipitation = f'Rain: {date["rain"]} mm Snow: {date["snow"]} mm'
        if date['rain'] < 5 and date['snow'] < 5:
          notify = None
        else:
          notify =  {'method': 'popup', 'minutes': 5 * 60}
      elif 'Rain' in weather_descript:
        emoji = '\U0001F327'
        precipitation = f'{date["rain"]} mm'
        if date['rain'] < 5:
          notify = None,
        else:
          notify = {'method': 'popup', 'minutes': 5 * 60}
      elif 'Snow' in weather_descript:
        emoji = '\U00002744'
        precipitation = f'{date["snow"]} mm'
        if date['snow'] < 5:
          notify = None
        else:
          notify = {'method': 'popup', 'minutes': 5 * 60}

      # High & Low Temperatures
      high_t = (f'High: {date["temp"]["max"]}\u00b0C')
      low_t = (f'Low: {date["temp"]["min"]}\u00b0C')

      # Event name for gCAL
      event_name = f'{emoji} {weather_descript} | {precipitation} | {high_t} {low_t}'

      # Feels like temperatures for description
      feels_like = ['<b>Feels Like:</b>']

      for time, temp in date['feels_like'].items():
        feels_like.append(f'{time.title()}: {temp}\u00b0C')

      # Convert 'feels_like' list to one string as
      # gCAL only saving the first list item to description
      # then add HTML for gCAL formatting
      description = ', '.join(feels_like).replace(', ', '<br>')

      # Add Weather Info as Event
      event = {
        'summary': event_name,
        'start': {
          'date': day
        },
        'end': {
          'date': end_day
        },
        'reminders': {
          'useDefault': False,
          'overrides': [
            notify,
          ],
        },
        # Transparency sets busy/available status,
        # Transparent means available.
        'transparency': 'transparent',
        'description': description
      }

      print(f'Verifying eventID via dates:')
      # Check if event exists in Google Calendar
      now = timestamp + timedelta(days = -1)
      # Convert now to ISO + TimeZone
      now = now.isoformat() + '-05:00'
      # By seeing if anything exists from current day forwards
      # Check if any events occuring on {day} or after {day}:
      events_result = service.events().list(calendarId=cal_id, timeMin=now, maxResults=2, singleEvents=True, orderBy='startTime').execute()
      events = events_result.get('items', [])
      # If events is empty, add weather event
      if events == []:
        event = service.events().insert(calendarId=cal_id, body=event).execute()
        print(f'Created {event_name}.')
      # Else, attempt to update the event
      else:
        for update_event in events:
          # If there is a matching event, with "mm" in event name update:
          if update_event['start']['date'] == day and 'mm' in update_event['summary']:
            print(f"OWM {day} == gCAL: {update_event['start']['date']}.")

            # Get eventID
            event_id = (update_event['id'])

            # Items to update:
            update_event['summary'] = event_name
            update_event['reminders'] = event['reminders']
            update_event['description'] = event['description']

            # Tell gCAL to update the event
            updating_event = service.events().update(calendarId=cal_id, eventId=event_id, body=event).execute()

            # Print the updated date.
            print(f"Updated {day}\n> {update_event['summary']}.")
            print(f"> Reminders: {update_event['reminders']}")
            print(f"> Description: {update_event['description']}")
            break
            # break or it'll continue to the else section
          else:
            print(f"OWM {day} != gCAL: {update_event['start']['date']}.")
            # Date doesn't match any event, loop and check next day
            continue
        else:
          # If we have upcoming events but they aren't for this OWM date,
          # Create an event
          event = service.events().insert(calendarId=cal_id, body=event).execute()
          print(f'Created {event_name}.')

        # Clear feels_like list for next event
        feels_like.clear()
    else:
      print(f'No precipitation for {day}.')

      # Check Google Calendar
      now = timestamp + timedelta(days = 1)
      now = now.isoformat() + '-05:00'
      # If any events occuring on {day} or after {day}:
      events_result = service.events().list(calendarId=cal_id, timeMin=now, maxResults=1, singleEvents=True, orderBy='startTime').execute()
      events = events_result.get('items', [])

      print(f'Checking if event already exists for deletion.')
      # If event exists, delete event
      for update_event in events:
        # If there is a matching event, with "mm" in event name update:
        if update_event['start']['date'] == day and 'mm' in update_event['summary']:
          print(f"OWM {day} == gCAL: {update_event['start']['date']}.")
          print('Event found with matching date and precipitation.')
          # Get eventID
          event_id = (update_event['id'])

          # Delete event
          service.events().delete(calendarId=cal_id, eventId=event_id).execute()
          print(f"Event for {update_event['start']['date']} deleted.")
          break
        else:
          print(f"> Next weather event is on {update_event['start']['date']}.")
          print(f"OWM {day} != {update_event['start']['date']}")
          continue
      print(f"> No weather events found on {day} for deletion.")

print('\nFinished adding precipitation to calendar.')
