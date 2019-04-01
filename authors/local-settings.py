from .settings import * 
import os

DEBUG = os.getenv('DJANGO_DEBUG', True)
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', '7pgozr2jn7zs_o%i8id6=rddie!*0f0qy3$oy$(8231i^4*@u3')
