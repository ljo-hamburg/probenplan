import re

from django import template
from django.utils import html
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='location', is_safe=True)
def format_location(location):
    if not location:
        return location
    components = re.split('[,\n]', location)
    components = [html.escape(string.strip()) for string in components]
    components[0] = "<strong>" + components[0] + "</strong>"
    new_location = components[0] + "<br />" + ", ".join(components[1:])
    return mark_safe(new_location)


@register.simple_tag
def extra_classes(event):
    classes = []
    if 'Konzert' in event.title or \
            'Generalprobe' in event.title:
        classes.append('important')
    if 'Dozentenprobe' in event.title:
        classes.append('special')
    if 'Vorstandssitzung' in event.title or \
            'Vollversammlung' in event.title:
        classes.append('orga')
    return mark_safe(' '.join(classes))
