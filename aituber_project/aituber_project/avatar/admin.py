from django.contrib import admin
from .models import User, ShortTermMemory, LongTermMemory

admin.site.register(User)
admin.site.register(ShortTermMemory)
admin.site.register(LongTermMemory)