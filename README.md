# Weather Calendar
I wanted a more customizable option to what IFTTT's version of `If this (rain/snow) than that (add Google Calendar event)`. My version provides type of precipitation (e.g. Thunder, Light Rain, Snow, etc), precipitation amount (in mm) and temperature for the day. It is added as an all-day event to Google Calendar with the ability to send a push notification to the user when rain is expected to be more than 5mm.

## Table of Contents
- [Built With](#Built-With)
- [Current Features](#Current-Features)
- [Future Goals](#Future-Goals)
- [License](#License)
- [Donations (Optional)](#Donations-(Optional))

## Built With
- [Python 3.8](python.org) with the help these Python modules:
- [Open Weather Map API](openweathermap.org/)
- [Google Calendar API](developers.google.com/calendar)

## Current Features
- Calls the OpenWeatherMap api
- Pulls the weather forecast related to precipitation for the next 7 days
- Adds precipitation information as a full day event to Google Calendar
    - Information included:
        - Type of precipitation (e.g. Thunder, Light Rain, Snow, etc)
        - How much precipitation expected (in mm)
        - If precipitation is greater than 5mm, send a notification the night before
        - Forecasted High and Low (in °C) for the day
        - Feels like temperature (in °C) for the entire day
- When it runs, it will check if there is already a weather event and update it (including weather to add or remove a notification for the night before).
- If a forecasted day for precipitation no longer has precipitation, it will delete the event.

## Future Goals:
- Add weather alerts/advisories

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Donations (Optional)
Ko-fi is basically a virtual tip jar where you can support creatives for about the price of a cup of coffee.

At this time, I'm not very active on Ko-fi nor do I offer any rewards. If you love my work and feel like supporting me, hit the button below to get started.

Tipping is optional but I will appreciate any amount you choose to donate. Thank you (´• ω •`) ♡ !

[![ko-fi](https://www.ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/I2I77G74)
