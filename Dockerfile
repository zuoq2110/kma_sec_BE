FROM python:3.9-slim-buster

WORKDIR /app

RUN pip install --no-cache-dir gunicorn==20.1.0

RUN addgroup -gid 1000 kma

RUN adduser --uid 1000 hieubm --ingroup kma

RUN chown -R hieubm:kma /app

USER hieubm

COPY --chown=hieubm:kma requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY --chown=hieubm:kma . /app/

CMD [ "gunicorn", "src.main:app" ]