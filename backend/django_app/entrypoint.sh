#!/bin/sh
set -e
python manage.py migrate --noinput
python manage.py shell <<'PY'
import os
from django.contrib.auth import get_user_model
User=get_user_model()
u=os.getenv('ADMIN_USERNAME','admin')
p=os.getenv('ADMIN_PASSWORD','Admin@12345')
e=os.getenv('ADMIN_EMAIL','admin@example.com')
if not User.objects.filter(username=u).exists():
    User.objects.create_superuser(username=u,email=e,password=p)
PY
exec python manage.py runserver 0.0.0.0:8000
