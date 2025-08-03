import json
import os
from datetime import date, datetime
from string import Template

from utilities.helper import assignmentRequest
from utilities.helper import wikiRand
from utilities.helper import eventsToday
from utilities.helper import weather
from utilities.helper import dishRand

__location__ = os.path.dirname(os.path.abspath(__file__))

# Datum
def get_date():
    return date.today().strftime("%d.%m.%Y")

def get_dayOfWeek():
    dow = date.today().strftime("%A")
    with open(os.path.join(__location__, "ressource/weekdayDict.json"), "r") as f:
        data = json.load(f)
        dow = data['Weekday'].get(dow, dow)
    return dow

# Wetterdaten holen
def get_weather(location):
    forecast = weather.get_weather(location)
    temp = forecast['TEMP']
    feels = forecast['FEELS']
    desc = forecast['DESC']
    min_ = forecast['MIN']
    max_ = forecast['MAX']
    return temp, feels, desc, min_, max_

# Kalenderdaten holen
def get_appointments(calendar):
    return assignmentRequest.getAssignments(calendar)

# Aktienmarkt-Daten (Platzhalter)
def get_stockData():
    return ""


# Hauptfunktion: generiert den HTML-Newsletter-Text
def send_newsletter(config: dict) -> str:
    LOCATION = config.get("place", "Berlin")
    CALENDAR = config.get("calendar", "")
    NAME = config.get("name", "Max")

    try:
        # Wetter
        todayweather = get_weather(LOCATION)

        # Termine
        appointments = ""
        if CALENDAR != 'nein':
            appointments = get_appointments(CALENDAR)

        # Events
        events = eventsToday.getEvents(LOCATION)

        # Wiki-Artikel
        wiki = wikiRand.main()

        # Rezept
        dish = dishRand.getRecipe()

        # Templates laden
        with open(os.path.join(__location__, "ressource/telegramTemplate.txt"), "r", encoding="utf-8") as f:
            telegram_template = Template(f.read())

        with open(os.path.join(__location__, "ressource/contentDict.json"), "r", encoding="utf-8") as f:
            snipped = json.load(f)

        # Wetter-Snippet
        if todayweather:
            with open(os.path.join(__location__, "ressource/weatherDict.json"), "r", encoding="utf-8") as f:
                weatherData = json.load(f)
            weatherDesc = weatherData['Weather'].get(todayweather[2], todayweather[2])

            weatherSnipped = Template(snipped['WEATHER']).safe_substitute(
                location=LOCATION,
                feels=todayweather[1],
                desc=weatherDesc,
                temp=todayweather[0],
                min=todayweather[3],
                max=todayweather[4]
            )
        else:
            weatherSnipped = ""

        # Kalender
        if appointments:
            calendarSnipped = Template(snipped['CALENDAR']).safe_substitute(
                appointmentsToday=appointments
            )
        else:
            calendarSnipped = ""

        # Wiki
        if wiki:
            wikiSnipped = Template(snipped['WIKI']).safe_substitute(
                wikiUrl=wiki['Link'],
                wikiText=wiki['Header']
            )
        else:
            wikiSnipped = ""

        # Gericht
        if dish:
            dishSnipped = Template(snipped['DISH']).safe_substitute(
                dishUrl=dish['Link'],
                dishText=dish['Title'],
                dishImg=dish['Img']
            )
        else:
            dishSnipped = ""

        # Events
        if events:
            eventsSnipped = Template(snipped['EVENTS']).safe_substitute(
                eventsToday=events,
                location=LOCATION
            )
        else:
            eventsSnipped = ""

        # Alles zusammenbauen
        content = telegram_template.safe_substitute(
            name=NAME,
            dow=get_dayOfWeek(),
            date_today=get_date(),
            weatherTemplate=weatherSnipped,
            appointmentsTemplate=calendarSnipped,
            wikiTemplate=wikiSnipped,
            dishTemplate=dishSnipped,
            eventsTemplate=eventsSnipped
        )

        return content

    except Exception as e:
        return f"<b>Fehler beim Generieren des Newsletters:</b> {str(e)}"

