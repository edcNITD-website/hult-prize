from django.contrib import admin
from .models import *

admin.site.register(Category)
admin.site.register(Choice)
admin.site.register(UserResponse)
admin.site.register(Leaderboard)

class Answeradmin(admin.StackedInline):
    model=Choice

class QuestionAdmin(admin.ModelAdmin):
    inlines=[Answeradmin]

admin.site.register(Question,QuestionAdmin)

