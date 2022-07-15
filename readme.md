# FAST VOTE WEB APP
==================
This web app allows users to register to vote and create elections.


## INSTALLATION
=================
For the web app to run well, run the following commands:
* virtualenv venv
    * /venv/Scripts/activate (Windows Only)
    * source venv/bin/activate (linux/MacOS)
* pip install -r requirements.txt
* 0351791731celery -A core worker -l info (starts celery)
* python manage.py makemigrations
* python manage.py migrate
* python manage.py createsuperuser
* python manage.py runserver

#### NOTE: RUN THE COMMANDS IN THE ABOVE FORMAT



