FROM python:3-alpine

ENV PYTHONUNBUFFERED 1
ARG PROBENPLAN_CALENDAR=none

RUN mkdir /code
WORKDIR /code
COPY . /code/
RUN apk update \
	&& apk add dcron wget rsync ca-certificates \
	&& apk add dcron wget rsync ca-certificates build-base \
    && pip install -r requirements.txt \
    && mkdir static \
    && python manage.py migrate \
    && python manage.py compilescss \
    && python manage.py collectstatic \
    && rm -rf /var/cache/apk/* \
    # Configure Crontab
    && mkdir -p /var/log/cron \
	&& mkdir -m 0644 -p /var/spool/cron/crontabs \
	&& touch /var/log/cron/cron.log \
	&& mkdir -m 0644 -p /etc/cron.d \
	# Configure Cronjobx
	&& /usr/bin/crontab /code/crontab.txt

EXPOSE 8000

CMD ['/code/entry.sh']

