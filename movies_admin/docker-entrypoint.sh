#!/usr/bin/env bash

set -e

python manage.py migrate
python manage.py collectstatic --no-input

./wait-for-it.sh db:5432 --strict -- uwsgi --strict --ini uwsgi.ini