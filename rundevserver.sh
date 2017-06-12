#! /bin/bash

## Start the Python server
DJANGO_PORT=${1:-8002}
DJANGO_SETTINGS_MODULE=tutorons.settings.dev python manage.py runserver $DJANGO_PORT

# Shutdown all servers when on interrupt
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT
