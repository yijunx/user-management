#! /bin/bash

clear
source ./admin_user.env
pytest -v --cov-report term --cov=app