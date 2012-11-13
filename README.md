Compile Instructions
======

The following instructions are assuming use of Ubuntu 12.4 or later. 

Prerequists
-----------

* Git
* Python 2.7
* Python Developer Libraries
* Python Setuptools
* Postgresql 9.1
* Postgresql Server Dev
* Postgres PostGIS
* Postgis
* Binutils
* Libproj Dev
* GDAL
* Scientific Python
* south

Install system prerequisits with apt-get
----------------------------------------

    apt-get install python python-dev git python-setuptools postgresql-9.1 postgresql-server-dev-9.1 postgresql-9.1-postgis postgis binutils libproj-dev gdal-bin python-scipy 

Install Postgis template in Postgres
------------------------------------

Download and execute this script - https://docs.djangoproject.com/en/dev/_downloads/create_template_postgis-debian1.sh

Create the CATAMI database, and users
-------------------------------------

    su postgres
    createuser -U postgres pocock
    createdb -T template_postgis Force
    psql
    "alter user pocock with password '<your password here>'";

Allow access to Postgres remotely
---------------------------------

    vim /etc/postgresql/9.1/main/pg_hba.conf
    "local	all	pocock md5"
    "host		all	all	0.0.0.0/0	md5"
    /etc/init.d/postgresql restart

Install and configure virtualenv, virtualenvwrapper and pip
-----------------------------------------------------------

    easy_install virtualenv
    easy_install virtualenvwrapper
    easy_install pip
    vim .bashrc
    "export WORKON_HOME=$HOME/.virtualenvs"
    "source /usr/local/bin/virtualenvwrapper.sh"
    source .bashrc

Create a virtual environment for the catami project (so we don't mess up the system libraries with the catami versions)
-----------------------------------------------------------------------------------------------------------------------

    mkvirtualenv catami --system-site-packages
    workon catami

Checkout the code and GO!
-------------------------

    git clone https://github.com/catami/catami.git
    cd catami
    pip install -r requirements.txt
    ./manage.py syncdb
    ./manage.py schemamigration Force --initial
    ./manage.py migrate Force --auto
    ./manage.py runserver
