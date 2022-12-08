import os
from .base import *

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

DEBUG = False
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

ALLOWED_HOSTS = ['*']