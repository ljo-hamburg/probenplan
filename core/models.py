from django.db import models
import arrow


class EventList:
    """
    An instance of this class represents a list of events that are associated with a specific date (most commonly a
    single day).
    """
    day: arrow
    events: list

    def __init__(self, day=None, events=None):
        """
        Creates a new instance with the specified `day` and `events`.
        :param day: An arrow instance identifying the day represented by the instance.
        :param events: A collection of events. The event will be sorted automatically.
        """
        self.day = day
        if events:
            self.events = sorted(events, key=lambda e: (not e.all_day, e.begin))

    @property
    def has_timed_events(self):
        """
        Returns a boolean value indicating whether the `EventList` contains events that are not all-day events.
        """
        for event in self.events:
            if not event.all_day:
                return True
        return False


class Event(models.Model):
    """
    An events represents an entry in the schedule.
    """

    class Meta:
        ordering = ('begin',)

    begin = models.DateTimeField()
    end = models.DateTimeField()
    title = models.TextField()
    location = models.TextField()
    description = models.TextField(help_text="The location should consist of multiple comma separated elements. E.g. "
                                             "'venue, street, town'")
    all_day = models.BooleanField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.all_day:
            return self.title + " (whole day)"
        else:
            return self.title + " ({:%d. %b %Y})".format(self.begin)

    @staticmethod
    def timeline(from_date=None, to_date=None, all_events=False):
        """
        Returns an array of `EventList` objects identifying all events in the specified time frame. If no time frame is
        given, all future events are considered.
        :param from_date: The earliest date for events to be included.
        :param to_date: The latest date for events to be included.
        :param all_events: If `True` `from_date` and `to_date` are ignored and all events (including past events) are
         considered.
        :return: An array of `EventList` objects identifying the relevant events.
        """
        events = Event.objects.all()
        if not all_events and from_date:
            events = events.filter(end__gte=arrow.get(from_date).datetime)
        elif not all_events and not from_date:
            events = events.filter(end__gte=arrow.now().datetime)
        if not all_events and to_date:
            events = events.filter(begin__lte=arrow.get(to_date).datetime)

        day_events = {}
        for event in events:
            for date in arrow.Arrow.range('day', event.begin, event.end):
                floored = date.floor('day')
                if date == event.end:
                    continue
                if floored not in day_events:
                    day_events[floored] = set()
                day_events[floored].add(event)
        return [EventList(day, events) for (day, events) in day_events.items()]


class EventColorDescription(models.Model):
    """
    An event color description maps a color to a textual description that is displayed at the top of the schedule.
    """

    class Meta:
        ordering = ('index',)

    color = models.TextField(choices=[
        ('red', 'Red'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('gray', 'Gray')
    ], null=False, unique=True)
    description = models.TextField()
    index = models.IntegerField(help_text="The index determines the order in which colors are displayed.", unique=True)

    def __str__(self):
        return self.color + ": " + self.description


class EventColorMapping(models.Model):
    """
    An event color mapping maps a regular expression to a `EventColorDescription`. The regex is applied to an event's
    title to determine whether the specified color should be applied to the event.
    """

    class Meta:
        ordering = ("color__index",)

    regex = models.TextField(help_text="The RegEx is applied to an event's title.")
    case_sensitive = models.BooleanField(help_text="Whether to perform a case sensitive RegEx search.", default=True)
    color = models.ForeignKey(EventColorDescription, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return '"' + self.regex + '": ' + self.color.color
