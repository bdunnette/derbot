#!/bin/bash

NAME="derbot-huey"  # Name of the application
DJANGODIR=/home/dunn0172/code/derbot  # Django project directory
DJANGOENVDIR=/home/dunn0172/.virtualenvs/derbot-NRWX0B-6  # Django project virtualenv

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $DJANGODIR
source $DJANGOENVDIR/bin/activate
source $DJANGODIR/.env
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Start Huey
exec ${DJANGOENVDIR}/bin/python manage.py run_huey
