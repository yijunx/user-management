#! /bin/bash

clear
source ./sendgrid.env
source ./admin_user.env
pytest -v --cov-report term --cov=app