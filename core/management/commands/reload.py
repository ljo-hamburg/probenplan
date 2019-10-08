import os
from urllib.request import urlopen

from django.core.management.base import BaseCommand, CommandError
from ics import Calendar

from Probenplan import settings
from core.models import Event


class Command(BaseCommand):
    help = 'Reloads data for the Schedule from the remote source specified in the environment variable ' \
           '$PROBENPLAN_CALENDAR'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        url = os.getenv('PROBENPLAN_CALENDAR')
        if not url:
            raise CommandError('Environment Variable PROBENPLAN_CALENDAR is not set.')
        calendar = Calendar(urlopen(url).read().decode())
        Event.objects.all().delete()
        events = []
        for entry in calendar.timeline:
            event = Event()
            event.title = entry.name
            event.location = entry.location
            event.description = entry.description
            event.begin = entry.begin.to(settings.TIME_ZONE).datetime
            event.end = entry.end.to(settings.TIME_ZONE).datetime
            event.all_day = entry.all_day
            events.append(event)
        Event.objects.bulk_create(events)
