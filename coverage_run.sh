#!/bin/sh
set -e  # Configure shell so that if one command fails, it exits

docker-compose -f local.yml run --rm django coverage erase &&
docker-compose -f local.yml run  --rm django coverage run manage.py test &&
docker-compose -f local.yml run --rm django coverage html
