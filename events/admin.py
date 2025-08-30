from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Event, EventRegistration

# Register your models here.
admin.site.register(CustomUser, UserAdmin)
admin.site.register(Event)
admin.site.register(EventRegistration)
