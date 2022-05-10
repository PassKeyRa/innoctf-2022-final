FROM python:3.7.3-alpine as build
RUN apk update && apk add build-base gcc postgresql-dev

WORKDIR /usr/app
RUN python -m venv /usr/app/venv
ENV PATH="/usr/app/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

FROM python:3.7.3-alpine

RUN apk update && apk add netcat-openbsd postgresql-dev libc6-compat

RUN adduser -D python && \
    addgroup python python

RUN mkdir /usr/app && chown python:python /usr/app
WORKDIR /usr/app

COPY --chown=python:python --from=build /usr/app/venv ./venv
COPY --chown=python:python app app
COPY --chown=python:python uploads uploads
COPY --chown=python:python config.py entrypoint.sh requirements.txt task.py ./
RUN chmod +x /usr/app/entrypoint.sh

USER python

ENV PATH="/usr/app/venv/bin:$PATH"
ENTRYPOINT  [ "/usr/app/entrypoint.sh" ]
