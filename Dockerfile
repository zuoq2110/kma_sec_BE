FROM python:3.9-slim-buster

RUN apt-get update && \
    apt-get install -y openjdk-11-jre-headless && \
    apt-get clean;

RUN pip install --no-cache-dir --upgrade gunicorn==20.1.0

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt;

COPY . /app/

CMD [ "gunicorn", "src.main:app" ]