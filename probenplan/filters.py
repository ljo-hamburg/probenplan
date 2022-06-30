"""
This module provides filters that can be used in Jinja templates.
"""

import html
import re
from typing import Dict, Iterable, List

from arrow import Arrow
from ics import Event
from markdown import markdown as md

from . import Config
from .app import app

config = Config.instance()
LOCATION_SEPARATOR = re.compile("[,\n]")
TEAMS_SEPARATOR = re.compile("_{10,}")


@app.template_filter()
def group_by_day(events: Iterable[Event]) -> Dict[Arrow, List[Event]]:
    """
    Returns a dict of lists of events representing a grouping by day. Each entry
    in the dictionary corresponds to the events of a single day. Only days with
    at least one event will be included in the dictionary.

    :param events: An iterable of events.
    :return: A grouping of events by days.
    """
    day_events = {}
    for event in events:
        for date in Arrow.range("day", event.begin, event.end):
            if date == event.end:
                # This happens on all-day events that last until 00:00 on the end date.
                continue
            floored = date.floor("day")
            day_events.setdefault(floored, [])
            day_events[floored].append(event)
    return day_events


@app.template_filter()
def datetime(value: Arrow,
             fmt: str = "YYYY-MM-DD HH:mm:ssZZ",
             locale: str = None) -> str:
    """
    Formats the datetime `value` with the specified `fmt` format string.

    :param value: The datetime value to be formatted.
    :param fmt: The format string used for formatting.
    :param locale: The locale used for formatting.
    """
    return value.format(fmt, locale=locale or config.locale)


@app.template_filter()
def location(event: Event) -> str:
    """
    Formats the location of an event. This highlights the first row.
    :param event: The event whose location is to be highlighted.
    :return: A HTML encoded string that is safe to render.
    """
    if not event.location:
        return ""
    components = LOCATION_SEPARATOR.split(event.location)
    components = [
        html.escape(string.strip()).encode('ascii', 'xmlcharrefreplace').decode()
        for string in components
    ]
    components[0] = "<strong>" + components[0] + "</strong>"
    return components[0] + "<br />" + ", ".join(components[1:])


@app.template_filter()
def markdown(value: str) -> str:
    """
    Renders the specified `value` as markdown.
    :param value: The Markdown text.
    :return: An HTML representation of `value`.
    """
    return md(value)
