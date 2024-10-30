from django.contrib import admin
from .models import *

admin.site.register(Question)
admin.site.register(Category)
admin.site.register(Choice)
admin.site.register(UserResponse)
admin.site.register(Leaderboard)
