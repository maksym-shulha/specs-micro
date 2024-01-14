FROM python:latest

RUN apt-get update && apt-get install -y \
    cron \
    supervisor

WORKDIR /specs_micro

COPY ./requirements.txt /specs_micro/requirements.txt
COPY ./supervisord.conf /specs_micro/supervisord.conf

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./specs_micro/. /specs_micro

RUN mkdir log_files

ADD ./crontab /etc/cron.d/my-cron-file
RUN crontab /etc/cron.d/my-cron-file

EXPOSE 8001
