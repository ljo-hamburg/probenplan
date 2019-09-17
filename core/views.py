import datetime
import os
import re

import arrow
from django.shortcuts import render
from django.utils import html
from django.views.decorators.clickjacking import xframe_options_exempt
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

    @property
    def css_classes(self):
        classes = []
        if self.title == "Vorstandssitzung":
            classes.append('vorstandssitzung')
        if self.title == "Vollversammlung":
            classes.append('vollversammlung')
        if self.title.startswith('Neu:'):
            classes.append('new')
        return classes


class DayEvents:
    day: arrow
    events: list

    @property
    def has_timed_events(self):
        for event in self.events:
            if not event.all_day:
                return True
        return False


@xframe_options_exempt
def probenplan(request):
    all_events = request.GET.get('all', 'false').lower() in ['true', '1', 'yes', 'on']
    black_and_white = request.GET.get('bw', 'false').lower() in ['true', '1', 'yes', 'on']
    from_date = request.GET.get('from', None)
    to_date = request.GET.get('to', None)

    if from_date:
        from_date = arrow.get(from_date)
    if to_date:
        to_date = arrow.get(to_date)

    url = os.getenv('PROBENPLAN_CALENDAR')
    calendar = Calendar(urlopen(url).read().decode())
    events = []
    for day in get_relevant_days(request, calendar, from_date, to_date):
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
        'from_date': from_date,
        'to_date': to_date,
        'black_and_white': black_and_white,
        'all_events': all_events,
        'today': arrow.now(tz=settings.TIME_ZONE),
        'events': events
    })


def get_relevant_days(request, calendar, from_date, to_date):
    all_events = request.GET.get('all', 'false').lower() in ['true', '1', 'yes', 'on']

    days = set()
    if all_events:
        timeline = calendar.timeline
    elif from_date:
        timeline = calendar.timeline.start_after(from_date)
    else:
        timeline = calendar.timeline.start_after(arrow.now(tz=settings.TIME_ZONE))
    for event in timeline:
        if to_date and event.begin > to_date.ceil('day'):
            break
        for date in arrow.Arrow.range('day', event.begin, event.end):
            days.add(date.floor('day'))
    return sorted(days)


def clean_location(location):
    if not location:
        return location
    components = re.split('[,\n]', location)
    components = [html.escape(string.strip()) for string in components]
    components[0] = "<strong>" + components[0] + "</strong>"
    return components[0] + "<br />" + ", ".join(components[1:])
