#!/usr/bin/env sh

# start cron
/usr/sbin/crond

# Run Django
python manage.py runserver 0.0.0.0:8000