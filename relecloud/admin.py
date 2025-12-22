from django.contrib import admin
from . import models

admin.site.register(models.Cruise)
admin.site.register(models.Destination)
admin.site.register(models.InfoRequest)

# Apartado 3
admin.site.register(models.Opinion)
admin.site.register(models.UserTravelRecord)
admin.site.register(models.UserProfile)