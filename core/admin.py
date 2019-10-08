from django.contrib import admin

# Register your models here.
from core.models import *

admin.site.register(Event)
admin.site.register(EventColorDescription)
admin.site.register(EventColorMapping)
