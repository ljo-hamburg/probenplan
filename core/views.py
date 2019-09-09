import datetime
import os
import re

import arrow
from django.shortcuts import render
from django.utils import html
from ics import Calendar
from urllib.request import urlopen

from Probenplan import settings


class Event:
    begin: arrow
    end: arrow
    title: str
    location: str
    description: str
    all_day: bool


class DayEvents:
    day: arrow
    events: list

    @property
    def has_timed_events(self):
        for event in self.events:
            if not event.all_day:
                return True
        return False


def probenplan(request):
    url = os.getenv('PROBENPLAN_CALENDAR')
    calendar = Calendar(urlopen(url).read().decode())
    events = []
    days = set()
    timeline = calendar.timeline.start_after(arrow.now(tz=settings.TIME_ZONE))
    for event in timeline:
        for date in arrow.Arrow.range('day', event.begin, event.end):
            days.add(date.floor('day'))
    for day in sorted(days):

        my_day_events = []
        for event in calendar.timeline.on(day):
            if event.end == day:
                continue
            my_event = Event()
            my_event.title = event.name
            my_event.location = clean_location(event.location)
            my_event.description = event.description
            my_event.begin = event.begin.to(settings.TIME_ZONE)
            my_event.end = event.end.to(settings.TIME_ZONE)
            my_event.all_day = event.all_day
            my_day_events.append(my_event)
        day_events = DayEvents()
        day_events.day = day
        day_events.events = sorted(my_day_events, key=lambda e: (not e.all_day, e.begin))
        events.append(day_events)
    return render(request, 'core/probenplan.html', {
        'today': arrow.now(tz=settings.TIME_ZONE),
        'events': events
    })


def clean_location(location):
    # (.*) (Name of the Location)
    # ,    (Comma)
    # .*   (Street Name)
    #      (Space)
    # \d*  (House Number)
    # ,    (Comma)
    # \d+  (Postal Code)
    #      (Space)
    # \w*   (Town)
    if not location:
        return location
    components = location.split(",")
    components = [html.escape(string.strip()) for string in components]
    components[0] = "<strong>" + components[0] + "</strong>"
    return components[0] + "<br />" + ", ".join(components[1:])