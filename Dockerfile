FROM python:3-alpine

ENV PYTHONUNBUFFERED 1
ARG PROBENPLAN_CALENDAR=none

RUN apk update \
	# Add Dependencies
	&& apk add dcron wget rsync ca-certificates build-base \
	&& rm -rf /var/cache/apk/* \
	# Configure Crontab
    && mkdir -p /var/log/cron \
	&& mkdir -m 0644 -p /var/spool/cron/crontabs \
	&& mkdir -m 0644 -p /etc/cron.d \
	&& mkdir /code

WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY . /code/
RUN mkdir static \
    && python manage.py migrate \
    && python manage.py compilescss \
    && python manage.py collectstatic \
	# Configure Cronjobs
	&& echo '5 * * * * cd /code && python manage.py reload >> /var/log/probenplan-cron.log 2>&1' > /crontab.txt \
	&& /usr/bin/crontab /crontab.txt \
	&& rm -f /crontab.txt

EXPOSE 8000

ENTRYPOINT ["/code/entry.sh"]
