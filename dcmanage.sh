#!/bin/bash

sudo docker-compose run --rm poster-web python manage.py "$@"
