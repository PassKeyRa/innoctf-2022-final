#!/bin/bash

while ! nc -z postgres 5432; do sleep 3; done
while ! nc -z redis 6379; do sleep 3; done

#node index.js
npm start --host 0.0.0.0
