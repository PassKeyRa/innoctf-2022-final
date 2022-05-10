FROM node:14-alpine

RUN mkdir /app && apk add git

COPY app/package.json /app

WORKDIR /app

RUN npm install

COPY .secret /app
COPY app /app

RUN chmod +x start.sh

EXPOSE 8000

ENTRYPOINT /bin/sh /app/start.sh
