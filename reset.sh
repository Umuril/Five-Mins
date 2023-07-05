#!/bin/bash

##### SETUP PHASE #####
unzip -n static/ext/\*.zip -d static/ext/
##### SETUP PHASE #####


##### CLEAN UP PHASE #####
rm -fr static/ext/Fork-Awesome-1.2.0/{less,scss,src}
rm -f db.sqlite3
##### CLEAN UP PHASE #####


##### DJANGO PHASE #####
python3 manage.py makemigrations knock
python3 manage.py makemigrations
python3 manage.py migrate
DJANGO_SUPERUSER_USERNAME=root \
DJANGO_SUPERUSER_PASSWORD=toor \
DJANGO_SUPERUSER_EMAIL="root@example.com" \
python3 manage.py createsuperuser --noinput
##### DJANGO PHASE #####


##### CUSTOM PHASE #####
python3 manage.py init
python3 manage.py create_user -n 10
python3 manage.py create_worker -n 11
python3 manage.py create_knock -n 100
python3 manage.py create_submit -n 100
python3 manage.py reserve_knock -n 100
python3 manage.py progress_knock --wip -n 100
python3 manage.py progress_knock --done -n 100
python3 manage.py rate_knock -n 40
python3 manage.py runapscheduler
##### CUSTOM PHASE #####
