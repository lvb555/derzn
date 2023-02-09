# -*- coding: utf-8 -*-
import os, sys

sys.path.insert(0, "/var/www/u1353596/data/www/derzn.ru/dz")
sys.path.insert(
    1, "/var/www/u1353596/data/www/derzn.ru/venv/lib/python3.10/site-packages"
)
os.environ["DJANGO_SETTINGS_MODULE"] = "dz.settings"
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
