from django.db import models


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
