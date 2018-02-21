
#! bash script for setting up enviornment for flask app


sudo apt-get install python3-pip

sudo pip3 install virtualenv

virtualenv flask

#proxy="--proxy http://proxy.iiit.ac.in:8080 "

proxy=""

flask/bin/pip $proxy install flask

flask/bin/pip $proxy install flask-login

flask/bin/pip $proxy install requests

flask/bin/pip $proxy install requests

flask/bin/pip $proxy install bs4

flask/bin/pip $proxy install python-dateutil

flask/bin/pip $proxy install datetime

flask/bin/pip $proxy install -U flask-cors
