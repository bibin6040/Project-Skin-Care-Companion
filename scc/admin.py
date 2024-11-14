from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register((Registration,))
admin.site.register((admin_login,))
admin.site.register((PredictionRequest,))
admin.site.register((Contact,))