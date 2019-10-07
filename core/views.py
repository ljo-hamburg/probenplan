import arrow
from django.core.management import call_command
from django.shortcuts import render, redirect
from django.views.decorators.clickjacking import xframe_options_exempt

from Probenplan import settings
from core.models import Event


class EventList:
    day: arrow
    events: list

    @property
    def has_timed_events(self):
        for event in self.events:
            if not event.all_day:
                return True
        return False


# TODO: Auto Reload Mechanism
@xframe_options_exempt
def reload(request):
    call_command('reload')
    return redirect('/')


@xframe_options_exempt
def index(request):
    all_events = request.GET.get('all', 'false').lower() in ['true', '1', 'yes', 'on']
    black_and_white = request.GET.get('bw', 'false').lower() in ['true', '1', 'yes', 'on']
    from_date = request.GET.get('from', None)
    to_date = request.GET.get('to', None)

    events = Event.objects.all()
    if not all_events and from_date:
        events = events.filter(begin__gte=arrow.get(from_date).datetime)
    elif not all_events and not from_date:
        events = events.filter(begin__gte=arrow.now().datetime)
    if not all_events and to_date:
        events = events.filter(end__lte=arrow.get(to_date).datetime)

    day_events = {}
    for event in events:
        for date in arrow.Arrow.range('day', event.begin, event.end):
            floored = date.floor('day')
            if date == event.end:
                continue
            if floored not in day_events:
                day_events[floored] = set()
            day_events[floored].add(event)
    event_lists = []
    for (day, events) in day_events.items():
        event_list = EventList()
        event_list.day = day
        event_list.events = sorted(events, key=lambda e: (not e.all_day, e.begin))
        event_lists.append(event_list)
    event_lists = sorted(event_lists, key=lambda l: l.day)
    return render(request, 'core/probenplan.html', {
        'from_date': arrow.get(from_date) if from_date else None,
        'to_date': arrow.get(to_date) if to_date else None,
        'black_and_white': black_and_white,
        'all_events': all_events,
        'today': arrow.now(tz=settings.TIME_ZONE),
        'events': event_lists
    })
