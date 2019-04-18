echo "run migrations start"
python manage.py makemigrations authentication
python manage.py migrate authentication
python manage.py makemigrations auth
python manage.py migrate auth
python manage.py makemigrations profiles
python manage.py migrate profiles
python manage.py makemigrations follow
python manage.py migrate follow
python manage.py makemigrations articles
python manage.py migrate articles
python manage.py makemigrations comments
python manage.py migrate comments
python manage.py migrate
python manage.py syncdb
echo "Execution complete"