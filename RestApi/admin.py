from django.contrib import admin
from .models import User, Calendar, Event, GoogleUser
# Register your models here.

admin.site.register(User)
admin.site.register(Calendar)
admin.site.register(Event)
admin.site.register(GoogleUser)
