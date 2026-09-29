from django.contrib import admin
from .models import Card,Transaction,AdminLog
admin.site.register([Card,Transaction,AdminLog])
