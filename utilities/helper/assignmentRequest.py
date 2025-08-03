import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, time, timedelta
from dateutil.rrule import rrulestr
import requests
from icalendar import Calendar

import os.path

def getAssignments(ICS):


    response = requests.get(ICS)

    ical_data = response.text
    calendar = Calendar.from_ical(ical_data)

    today_min = datetime.combine(datetime.today(), time.min)
    today_max = datetime.combine(datetime.today(), time.max)
    tomorrow = datetime.combine(datetime.today() + timedelta(days=1), time.min)

    for event in calendar.walk("VEVENT"):
        start = event.get("DTSTART").dt
        end = event.get("DTEND").dt

        try:
            if not start.time():
                start = datetime.combine(start, datetime.min.time())
                end = datetime.combine(end, datetime.min.time())
        except:
            start = datetime.combine(start, datetime.min.time())
            end = datetime.combine(end, datetime.min.time())
        
        try:
            start = start.replace(tzinfo=None)
            end = end.replace(tzinfo=None)
        except:
            pass

        occurrences = ""
            
        if 'RRULE' in event:
            recurrence_rule = event['RRULE']
            rule = rrulestr(recurrence_rule.to_ical().decode())
            occurrences = [occ.replace(tzinfo=None) for occ in rule]

        if (today_min <= start <= today_max) or ([dt for dt in occurrences if today_min <= dt <= today_max]) :
            if start.time() == time.min:
                appointments = appointments + event.get("SUMMARY") + "\n\n"
            elif end >= tomorrow :
                appointments = appointments + event.get("SUMMARY") + " von: " + str(event.get("DTSTART").dt.strftime("%H:%M")) + " Uhr\n\n"
            else:
                appointments = appointments + event.get("SUMMARY") + " von: " + str(event.get("DTSTART").dt.strftime("%H:%M")) + " bis: " + str(event.get("DTEND").dt.strftime("%H:%M")) + " Uhr\n\n"
    
    # Remove last \n
    appointments = appointments[:-4]
    return appointments
