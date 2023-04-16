FROM python:3.9-slim-buster

RUN apt-get update && \
    apt-get install -y openjdk-11-jre-headless wget && \
    apt-get clean;

WORKDIR /app

RUN pip install --no-cache-dir gunicorn==20.1.0

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt;

COPY . /app/

CMD [ "gunicorn", "src.main:app" ]