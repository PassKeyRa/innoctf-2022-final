#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z db 5432; 
do
	sleep 0.1
done
echo "PostgreSQL started"

python task.py initdb
gunicorn -w 3 --bind 0.0.0.0:5000 task:app
exec "$@"
