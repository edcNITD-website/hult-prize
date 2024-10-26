from django.contrib import admin
from .models import Question, Choice, UserResponse, Crossword, Leaderboard

admin.site.register(Question)
admin.site.register(Crossword)
admin.site.register(Choice)
admin.site.register(UserResponse)
admin.site.register(Leaderboard)
