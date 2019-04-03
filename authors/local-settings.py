from .settings import * 
import os

DEBUG = os.getenv('DJANGO_DEBUG', True)
SECRET_KEY = os.getenv('SECRET_KEY')
