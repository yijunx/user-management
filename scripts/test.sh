#! /bin/bash

clear
source ./sendgrid.env
source ./admin_user.env
pytest --cov-report term --cov=app