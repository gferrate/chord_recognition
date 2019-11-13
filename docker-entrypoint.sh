#!/bin/sh
set -e
python3 manage.py collectstatic --noinput

if [ "$1" = 'uwsgi' ]; then
  #/usr/bin/python3 /app/src/manage.py migrate
  #exec python3 manage.py collectstatic --noinput
  #exec python3 manage.py migrate
  exec uwsgi --ini=/conf/uwsgi.ini
elif [ "$1" = 'rqworker' ]; then
  exec /usr/bin/python3 /app/manage.py rqworker $2 $3 $4
fi

exec "$@"
