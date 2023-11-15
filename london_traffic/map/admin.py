from django.contrib import admin

from .models import JamCam, Capture

# Register your models here.
admin.site.register(JamCam)
admin.site.register(Capture)
