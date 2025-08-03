import json, requests
from bs4 import BeautifulSoup
from string import Template 
import datetime as dt
from datetime import datetime
import os


def getEvents(location):

    URL = "https://www.regioactive.de/events/$locCode/$location/veranstaltungen-party-konzerte/$date"
    currentDay = dt.datetime.now().day
    currentMonth = dt.datetime.now().month
    currentYear = dt.datetime.now().year
    locCodeStr = ""

    __location__ = os.path.dirname(os.path.abspath(__file__))

    with open (__location__ + "/ressource/eventlocationDict.json", "r") as f:
        locCode = json.load(f)
        locCodeStr = locCode['Location'][location]
        f.close()

    URL = Template(URL).safe_substitute(location=location)
    URL = Template(URL).safe_substitute(date=str(currentYear)+"-"+str(currentMonth)+"-"+str(currentDay))
    URL = Template(URL).safe_substitute(locCode=locCodeStr)

    res = requests.get(URL)
    soup = BeautifulSoup(res.text, "lxml")
    
    divTag = soup.find_all("div", {"class": "media-body"})

    result = ""

    cName = ""
    cStart = ""
    cEnd = ""
    cLoc = ""

    for tag in divTag:
        # Überspringe gesponserte Events
        feature = tag.find_all("div", {"class": "featured"})
        if feature:
            continue

        # Suche die einzelnen Informationen
        name = tag.find_all("span", {"class": "summary"})
        dtStart = tag.find_all("span", {"class": "dtstart"})
        dtEnd = tag.find_all("span", {"class": "dtend"})
        loc = tag.find_all("span", {"class": "locstring"})

        # Werte extrahieren (fehlerresistent)
        try:
            cName = name[0].text.strip()
        except:
            cName = ""

        try:
            cStart = dtStart[0].text.strip().lower()
        except:
            cStart = ""

        try:
            cEnd = dtEnd[0].text.strip().lower()
        except:
            cEnd = ""

        try:
            cLoc = loc[0].text.strip()
        except:
            cLoc = ""

        # Heutiges Datum
        today = datetime.today().date()
        start_date = None
        end_date = None
        is_today = False

        # Sonderfall: "heute" als Text
        if "heute" in cStart or "heute" in cEnd:
            is_today = True
        else:
            # Versuche, Datumswerte zu parsen
            try:
                if cStart:
                    start_date = datetime.strptime(cStart, "%d.%m.%Y").date()
                if cEnd:
                    end_date = datetime.strptime(cEnd, "%d.%m.%Y").date()
            except:
                continue  # Ungültiges Datum -> überspringen

            # Prüfen, ob Event heute stattfindet
            if start_date:
                if end_date:
                    if start_date <= today <= end_date:
                        is_today = True
                else:
                    if today == start_date:
                        is_today = True

        if not is_today:
            continue  # Event ist nicht heute → überspringen

        # Original-Strings für die Ausgabe (Groß-/Kleinschreibung wiederherstellen)
        outputStart = dtStart[0].text.strip() if dtStart else ""
        outputEnd = dtEnd[0].text.strip() if dtEnd else ""
        outputLoc = cLoc

        textEnd = f" bis {outputEnd}" if outputEnd else ""
        textLoc = f" {outputLoc}" if outputLoc else ""

        itResult = f"{cName} {outputStart}{textEnd}{textLoc}\n"
        result = result + itResult + "\n"

    return(result)