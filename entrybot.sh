#!/bin/sh


DB_HOST="postgres"

DB_PORT="5432"

echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."

#
while ! nc -z $DB_HOST $DB_PORT; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - executing command"

exec "$@"