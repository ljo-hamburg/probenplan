#!/usr/bin/env sh

# start cron
/usr/sbin/crond -f -l 8

# Run Django
python manage.py runserver 0.0.0.0:8000