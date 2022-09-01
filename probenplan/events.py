from functools import cached_property
from typing import Iterable

import arrow
from arrow import Arrow

from . import config
from .graph import session as graph


class Event:
    def __init__(self, data: dict):
        self.subject: str = data.get("subject", "")
        self.description: str = data.get("bodyPreview", "")
        start = data.get("start", {}).get("dateTime")
        self.start: Arrow | None = arrow.get(start) if start else None
        end = data.get("end", {}).get("dateTime")
        self.end: Arrow | None = arrow.get(end) if end else None
        self.importance: str | None = data.get("importance")
        self.all_day: bool = data.get("isAllDay", False)
        self.location: str = data.get("location", {}).get("displayName", "")
        self.location_address: dict = data.get("location", {}).get("address", {})
        self.location_coordinates: dict = data.get("location", {}).get(
            "coordinates", {}
        )
        self.meeting_provider: str | None = data.get("onlineMeetingProvider")
        self.meeting_link: str | None = (data.get("onlineMeeting") or {}).get(
            "joinUrl"
        ) or data.get("onlineMeetingUrl")

    @cached_property
    def colors(self):
        return [
            index
            for (index, highlight) in enumerate(config.highlights)
            if highlight["pattern"].search(self.subject)
        ]

    @cached_property
    def is_heading(self):
        return self.subject.lstrip().startswith("--")

    @cached_property
    def heading(self):
        return self.subject.strip().removeprefix("--").removesuffix("--").strip()


def get_events(begin: Arrow | None, end: Arrow | None) -> Iterable[Event]:
    event_filter = f"end/dateTime ge '{begin.isoformat()}'"
    if end:
        event_filter += f" and start/dateTime le '{end.isoformat()}'"

    events = graph.get_list(
        f"users/{config.calendar_user}/calendar/events",
        params={
            "$filter": event_filter,
            "$orderby": "start/dateTime",
            "$top": 100,
        },
    )
    first = next(events, None)
    if not first:
        return
    first = Event(first)

    if not first.is_heading:
        heading = next(
            graph.get_list(
                f"users/{config.calendar_user}/calendar/events",
                params={
                    "$filter": (
                        f"startsWith(subject, '--') and "
                        f"start/dateTime le '{first.start.isoformat()}'"
                    ),
                    "$orderBy": "start/dateTime desc",
                    "$top": 1,
                },
            ),
            None,
        )
        if heading:
            yield Event(heading)
    yield first
    for event in events:
        yield Event(event)
