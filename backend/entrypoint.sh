#!/usr/bin/env bash
cd /opt/backend

if [ $INIT -eq 1 ]; then
    python ./manage.py makemigrations
    python ./manage.py migrate --fake-initial
    # use proxy to serve static files
    python ./manage.py collectstatic -v0 --noinput
    python setup.py sdist
    python setup.py develop
fi

# python ./manage.py runserver 0.0.0.0:8000
gunicorn --env DJANGO_SETTINGS_MODULE=backend.settings -b :8000 backend.wsgi