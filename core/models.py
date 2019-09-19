import arrow
from django.db import models


class Event(models.Model):
    begin = models.DateTimeField()
    end = models.DateTimeField()
    title = models.TextField()
    location = models.TextField()
    description = models.TextField()
    all_day = models.BooleanField()

    created_at = models.DateTimeField(auto_now_add=True)

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
