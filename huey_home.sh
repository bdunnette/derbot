#!/bin/bash

NAME="derbot-huey"  # Name of the application
DJANGODIR=$HOME/code/derbot  # Django project directory
DJANGOENVDIR=$HOME/.local/share/virtualenvs/derbot-zvsHdy7x  # Django project virtualenv

echo "`date` Starting $NAME as `whoami`"

# Activate the virtual environment
cd $DJANGODIR
source $DJANGOENVDIR/bin/activate
source $DJANGODIR/.env
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Start Huey
exec ${DJANGOENVDIR}/bin/python manage.py run_huey
