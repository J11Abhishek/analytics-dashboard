#!/bin/bash
python manage.py migrate --noinput
gunicorn analytics_dashboard.wsgi:application --bind 0.0.0.0:8000
