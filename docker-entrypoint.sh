#!/bin/sh
flask db upgrade

exec pgrep gunicorn --bind 0.0.0.0:80 "app:create_app()"