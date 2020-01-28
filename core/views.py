import arrow
from django.core.management import call_command
from django.shortcuts import render, redirect
from django.views.decorators.clickjacking import xframe_options_exempt

from Probenplan import settings
from core.models import Event, EventColorDescription


@xframe_options_exempt
def reload(request):
    """
    Reloads all events from the remote ICS source. This view redirects to the default index view.
    :param request: The user's request. Currently ignored.
    :return: Redirects to '/'
    """
    call_command('reload')
    return redirect('/')


@xframe_options_exempt
def index(request):
    """
    Renders the schedule. The following GET arguments are supported:
    - `all`: If set to true the schedule will contain all past and future events.
    - `bw`: If set no colors are rendered.
    - `from`: An earliest date for events to be included.
    - `to`: A latest date for events to be included.
    :param request: The user's request.
    :return: The rendered schedule.
    """
    all_events = request.GET.get('all', 'false').lower() in ['true', '1', 'yes', 'on']
    black_and_white = request.GET.get('bw', 'false').lower() in ['true', '1', 'yes', 'on']
    from_date = request.GET.get('from', None)
    to_date = request.GET.get('to', None)

    return render(request, 'core/probenplan.html', {
        'from_date': arrow.get(from_date) if from_date else None,
        'to_date': arrow.get(to_date) if to_date else None,
        'black_and_white': black_and_white,
        'all_events': all_events,
        'today': arrow.now(tz=settings.TIME_ZONE),
        'events': Event.timeline(from_date=from_date, to_date=to_date, all_events=all_events),
        'color_descriptions': EventColorDescription.objects.order_by('index')
    })
