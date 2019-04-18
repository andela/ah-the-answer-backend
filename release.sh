echo "run migrations start"
python manage.py makemigrations authentication
python manage.py migrate authentication
python manage.py makemigrations auth
python manage.py migrate auth
python manage.py migrate
python manage.py syncdb
echo "Done"