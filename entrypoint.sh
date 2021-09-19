#!/bin/sh
set -e

gunicorn example_app:app --daemon
curl localhost:8000/info
