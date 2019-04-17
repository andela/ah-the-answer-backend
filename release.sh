echo "run migrations start"
python manage.py migrate --fake authentication zero
python manage.py makemigrations authentication comments follow profile
python manage.py migrate

echo "Done"