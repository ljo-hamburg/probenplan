"""
This module provides filters that can be used in Jinja templates.
"""

import html
import re
from collections import defaultdict
from typing import Dict, Iterable, List, Tuple
from urllib.parse import urlencode

from arrow import Arrow
from markdown import markdown as md

from . import config
from .app import app
from .events import Event

LOCATION_SEPARATOR = re.compile("[,\n]")
TEAMS_SEPARATOR = re.compile("_{10,}")


@app.template_filter()
def group_by_day(
    events: Iterable[Event],
) -> Dict[Arrow, Tuple[List[Event], List[Event]]]:
    """
    Returns a dict of lists of events representing a grouping by day. Each entry
    in the dictionary corresponds to the events of a single day. Only days with
    at least one event will be included in the dictionary.

    :param events: An iterable of events.
    :return: A grouping of events by days.
    """

    def item():
        return [], []

    day_events = defaultdict(item)
    for event in events:
        for date in Arrow.range("day", event.start, event.end):
            if date == event.end:
                # This happens on all-day events that last until 00:00 on the end date.
                continue
            floored = date.floor("day")
            if event.is_heading:
                day_events[floored][1].append(event)
            else:
                day_events[floored][0].append(event)
    return day_events


@app.template_filter()
def datetime(
    value: Arrow,
    fmt: str = "YYYY-MM-DD HH:mm:ssZZ",
    locale: str = None,
    timezone: str = None,
) -> str:
    """
    Formats the datetime `value` with the specified `fmt` format string.

    :param value: The datetime value to be formatted.
    :param fmt: The format string used for formatting.
    :param locale: The locale used for formatting.
    :param timezone: The timezone in which to display the date.
    """
    return value.to(timezone or config.timezone).format(
        fmt, locale=locale or config.locale
    )


@app.template_filter()
def location(event: Event) -> str:
    """
    Formats the location of an event. This highlights the first row.
    :param event: The event whose location is to be highlighted.
    :return: A HTML encoded string that is safe to render.
    """
    if not event.location:
        return ""

    loc_name: str
    loc_components = []

    if event.location_address:
        loc_name = event.location

        street = event.location_address.get("street")
        if street:
            loc_components.append(street)
        postal_code = event.location_address.get("postalCode", "")
        city = event.location_address.get("city", "")
        if postal_code or city:
            loc_components.append(postal_code + " " + city)
    else:
        opening = event.location.find("(")
        closing = event.location.find(")")
        if 0 <= opening < closing:
            loc_name = event.location[:opening].strip()
            loc_components = LOCATION_SEPARATOR.split(
                event.location[opening + 1 : closing].strip()
            )
        else:
            split = LOCATION_SEPARATOR.split(event.location)
            loc_name, loc_components = split[0], split[1:]

    params = {"api": "1", "query": loc_name + " " + " ".join(loc_components)}
    loc_name = xml_escape(loc_name)
    loc_components = [xml_escape(string) for string in loc_components]
    result = "<strong>"
    if loc_components:
        result += (
            '<a target="_blank" href="https://www.google.com/maps'
            f'/search/?{urlencode(params)}">{loc_name}</a>'
        )
    else:
        result += loc_name
    result += "</strong>"
    result += "<br />" + ", ".join(loc_components)
    return result


@app.template_filter()
def description(event: Event) -> str:
    desc = ""
    if event.meeting_link:
        if event.meeting_provider == "teamsForBusiness":
            text = "Teams-Meeting beitreten"
        else:
            text = "Dem Meeting beitreten"
        desc += (
            f'<a class="button button-small button-outline" target="_blank" '
            f'href="{event.meeting_link}">{text}</a>'
        )
        if event.meeting_provider == "teamsForBusiness":
            desc += """
<p><small>Das Meeting wird über Microsoft Teams durchgeführt. Am besten funktioniert die
Teilnahme, wenn man sich die <a target="_blank"
href="https://www.microsoft.com/de-de/microsoft-teams/download-app">Teams-App
herunterlädt</a>. Eine Teilnahme über den Browser ist aber auch möglich.</p></small>
                        """
    desc += md(event.description).strip()
    return desc


def xml_escape(value: str) -> str:
    return html.escape(value.strip()).encode("ascii", "xmlcharrefreplace").decode()


@app.template_filter()
def markdown(value: str) -> str:
    """
    Renders the specified `value` as markdown.
    :param value: The Markdown text.
    :return: An HTML representation of `value`.
    """
    return md(value)
