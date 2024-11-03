# hult-prize/quiz/urls.py
from django.urls import path, re_path
from .views import *

urlpatterns = [
    path('', quiz_home, name='quiz_home'),
    path('start/', start_quiz, name='start_quiz'),
    re_path(r'^question/(?P<question_id>[0-9a-f-]+)/$', display_question, name='display_question'),
    path('leaderboard', leaderboard, name='leaderboard'),
    path('finished/', quiz_finished, name='quiz_finished'),
]