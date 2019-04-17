echo "run migrations start"
python manage.py migrate --fake auth zero
python manage.py makemigrations authentication comments follow profile
python manage.py migrate

echo "Done"