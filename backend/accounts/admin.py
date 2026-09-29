from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User

admin.site.register(User, UserAdmin)

admin.site.site_header = "Administración de SIGRED"
admin.site.site_title = "SIGRED"
admin.site.index_title = "Administración del sistema"