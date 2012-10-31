#!/bin/bash

sudo -u postgres psql postgres
echo \\password postgres

./create_postgis_template.sh

sudo -u postgres createdb -T template_postgis Force