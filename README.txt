Install the following packages (in ubuntu 16.04) if not installed:
sudo apt-get update
sudo apt-get install apache2
sudo apt-get install mysql-server
sudo apt-get install python-dev
sudo apt-get install libmysqlclient-dev



Install and run Elasticsearch 2.0.0

Create virtual environment for python2.7
pip install requirements.txt

Edit settings.py as required to connect to database
Also set TEMPLATE_DIRS, STATICFILES_DIRS etc.

Sync the db
python manage.py syncdb

Run the server
python manage.py runserver
