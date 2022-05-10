FROM node:14-alpine AS builder

RUN apk add jq
RUN npm install -g truffle

ARG NETWORK

COPY deploy /deploy
WORKDIR /deploy

RUN npm install


RUN truffle migrate --network ${NETWORK} && cat build/contracts/SmartChat.json | jq -r '[.networks[] | .address][-1]' > address

FROM node:14-alpine

COPY app /app
WORKDIR /app
COPY --from=builder /deploy/address .

RUN npm install

#EXPOSE 1337

ENTRYPOINT npm start
