from django.contrib import admin

from .models import Alert, Make, Ad, CarModel

admin.site.register(Make)
admin.site.register(CarModel)
admin.site.register(Alert)
admin.site.register(Ad)
