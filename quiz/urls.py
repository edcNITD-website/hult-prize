# hult-prize/quiz/urls.py
from django.urls import path
from .views import quiz_home, start_quiz, display_question, quiz_finished

urlpatterns = [
    path('', quiz_home, name='quiz_home'),
]
