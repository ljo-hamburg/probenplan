import re

from django import template
from django.utils import html
from django.utils.safestring import mark_safe

from core.models import EventColorMapping

register = template.Library()


@register.filter(name='location', is_safe=True)
def format_location(location):
    """
    Formats a location in multiple lines, highlighting the main venue.

    More technically this filter splits a string by commas and newlines and renders the first component bold.
    :param location: A string.
    :return: A html-safe string that represents a formatted version of the `location`.
    """
    if not location:
        return location
    components = re.split('[,\n]', location)
    components = [html.escape(string.strip()) for string in components]
    components[0] = "<strong>" + components[0] + "</strong>"
    new_location = components[0] + "<br />" + ", ".join(components[1:])
    return mark_safe(new_location)


@register.filter(name='color_tags')
def colors_tags_for_event(event):
    """
    Returns a set of color identifies that are associated with the `event`. The colors are determined by applying the
    `EventColorMapping`s from the database to the title of the `event`.
    :param event: An `Event`
    :return: A set of strings.
    """
    tags = set()
    for mapping in EventColorMapping.objects.order_by('color__index').all():
        if mapping.color is None:
            continue
        if (mapping.case_sensitive and re.search(mapping.regex, event.title, re.IGNORECASE)) \
                or not mapping.case_sensitive and re.search(mapping.regex, event.title):
            tags.add(mapping.color.color)
    return tags

@register.filter(name='details', is_safe=True)
def render_teams(event):
    """
    Returns a formatted string that can be safely displayed when the description contains an MS Teams Meeting.
    """
    parts = re.split("_{10,}", event.description)
    cleaned_parts = []
    for part in parts:
        if part.strip() == "":
            continue
        if part.strip().startswith("Microsoft Teams-Besprechung"):
            match = re.search("<(https://teams.microsoft.com/l/meetup-join/.+)>", part)
            if match:
                link = match[1]
                part = f"""
                    Microsoft Teams-Meeting<br />
                    Am Computer oder über mobile App teilnehmen.<br />
                    <a href="{link}" target="_blank">Hier klicken, um der Besprechung beizutreten</a> &VerticalLine; <a href="https://aka.ms/JoinTeamsMeeting" target="_blank">Weitere Infos</a>
                """
            else:
                part = "No Match"
        else:
            # Match URLs
            p = re.compile('''[^<">]((ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?)[^< ,"'>]''', re.MULTILINE)

            for item in re.finditer(p, part):
                result = item.group(0)
                result = result.replace(' ', '')
                part = part.replace(result, '<a href="' + result + '">' + result + '</a>')
        cleaned_parts.append(part)
    return "<hr>".join(cleaned_parts)
