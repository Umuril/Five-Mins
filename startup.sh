#!/bin/bash

python3 -m venv .env
source .env/bin/activate
pip3 install -r requirements.txt
bash ./reset.sh
python3 manage.py runserver
