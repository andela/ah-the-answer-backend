from .settings import * 
import os

DEBUG = os.getenv('DJANGO_DEBUG', True)
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
