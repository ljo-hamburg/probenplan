#!/usr/bin/env sh

# start cron
/usr/sbin/crond

python manage.py migrate
python manage.py compilescss
python manage.py collectstatic

# Run Django
python manage.py runserver 0.0.0.0:8000
