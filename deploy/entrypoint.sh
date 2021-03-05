#!/bin/sh
nginx
uwsgi --ini=/app/uwsgi.ini
