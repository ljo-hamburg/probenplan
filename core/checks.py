import os

from django.core.checks import Error, register


@register()
def example_check(app_configs, **kwargs):
    errors = []
    if "PROBENPLAN_CALENDAR" not in os.environ:
        errors.append(Error(
            'PROBENPLAN_CALENDAR not specified.',
            hint='Set the environment variable PROBENPLAN_CALENDAR to an iCal compatible URL',
            obj=os.environ,
            id='probenplan.E001',
        ))
    return errors
