#! /bin/bash
(
  source venv/bin/activate &&
  DJANGO_SETTINGS_MODULE=tutorons.settings.dev \
    python manage.py test --failfast
)
