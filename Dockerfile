FROM python:3.12.7-slim

WORKDIR /app

COPY charts.parquet ./charts.parquet

COPY app.py .

COPY run.sh .

COPY mysql-connector-j-9.1.0.jar .

COPY crontab.txt /etc/cron.d/cron-job

RUN chmod +x ./run.sh

RUN crontab /etc/cron.d/cron-job

RUN touch /var/log/cron.log

CMD ["sh", "-c", "cron && tail -f /var/log/cron.log"]