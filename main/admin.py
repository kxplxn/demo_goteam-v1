from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Team)
admin.site.register(User)
admin.site.register(Board)
admin.site.register(Column)
admin.site.register(Task)
admin.site.register(Subtask)
