"""
This module contains utility functions used to display the Probenplan.
"""

__all__ = ["event_timeline", "custom_color_css"]

from functools import lru_cache
from urllib.request import urlopen

from cachetools import cached, TTLCache
from ics import Calendar, Event
from ics.timeline import Timeline

from probenplan.config import Config

config = Config.instance()


@cached(cache=TTLCache(128, ttl=config.cache_ttl))
def event_timeline() -> Timeline:
    """Returns all events in chronological order."""

    with urlopen(config.url) as response:
        calendar = Calendar(response.read().decode())
    for event in calendar.events:
        event.probenplan = probenplan_data(event)
    return calendar.timeline


def probenplan_data(event: Event) -> dict:
    """
    Returns the additional data for a signle event. This data is used during
    templating.

    :param event: The event to analyze.
    :return: A dictionary of data.
    """
    data = {
        "colors": [
            index for (index, highlight) in enumerate(config.highlights) if
            highlight["pattern"].search(event.name)
        ]
    }
    if config.heading_pattern:
        match = config.heading_pattern.search(event.name)
        try:
            data["heading"] = match.group("value")
        except IndexError:
            data["heading"] = match.group(0)
        except AttributeError:
            # No match
            data["heading"] = False
    return data


@lru_cache
def custom_color_css() -> str:
    """
    This method creates a CSS string from the configured highlighters.
    :return: A CSS document.
    """
    return "\n".join(
        f".custom-color-{index} {{--color: {highlight['color']}}}"
        for (index, highlight) in enumerate(config.highlights)
    )
