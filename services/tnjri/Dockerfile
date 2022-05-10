FROM ubuntu:22.04
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Moscow
RUN apt update && apt install -y libpq-dev netcat
COPY ./app /app
WORKDIR /app
RUN chmod +x ./entry.sh && \
    touch log.txt old.txt
CMD ./entry.sh
