#! /bin/bash

clear
source ./sendgrid.env
pytest --cov-report term --cov=app