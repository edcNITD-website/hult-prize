from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Question, Choice, UserResponse, Leaderboard
from datetime import datetime, timedelta
import pytz

IST = pytz.timezone('Asia/Kolkata')
QUIZ_START_TIME = IST.localize(datetime(2024, 11, 3, 19, 5, 0)) # Start time for the quiz
QUIZ_END_TIME = IST.localize(datetime(2024, 11, 3, 20, 30, 0))  # End time for the quiz
MAX_POINTS = 100  # Maximum points for each question

DEFAULT_DURATION = 30  # Default for MCQ
SHORT_TEXT_DURATION = 50  # Duration for fill-in-the-blank questions
LONG_TEXT_DURATION = 150  # Duration for long text questions (passages)

def get_question_duration(question):
    if question.question_type == 'mcq' and len(question.question_text) > 150:
        return LONG_TEXT_DURATION
    elif question.question_type == 'text':
        return SHORT_TEXT_DURATION
    return DEFAULT_DURATION

def quiz_home(request):
    return render(request, 'quiz/quiz_home.html')

def get_next_question(user):
    answered_questions = UserResponse.objects.filter(user=user).values_list('question', flat=True)
    questions = Question.objects.all().order_by('id').exclude(id__in=answered_questions)
    return questions.first() if questions.exists() else None

@login_required
def start_quiz(request):
    current_time = timezone.now()
    if current_time < QUIZ_START_TIME:
        return render(request, 'quiz/not_started.html', {'quiz': {'title': "Quiz", 'start_time': QUIZ_START_TIME}})
    
    first_question = get_next_question(request.user)
    if not first_question or current_time > QUIZ_END_TIME:
        return redirect('quiz_finished')
    return redirect('quiz:display_question', question_id=first_question.id)

@login_required
def display_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    questions = Question.objects.all().order_by('id')
    question_index = list(questions).index(question)
    
    question_duration = get_question_duration(question)
    question_start_time = QUIZ_START_TIME + timedelta(seconds=question_duration * question_index)
    time_remaining = max(0, question_duration - int((timezone.now() - question_start_time).total_seconds()))
    
    next_question = questions[question_index + 1] if question_index + 1 < len(questions) else None
    time_is_up = (time_remaining == 0)
    if time_is_up:
        if next_question:
            return redirect('quiz:display_question', question_id=next_question.id)
        else:
            return redirect('quiz_finished')
    
    if request.method == 'POST' and not UserResponse.objects.filter(user=request.user, question=question).exists():
        points = min(100,max(0, int((time_remaining / question_duration) * MAX_POINTS)))
        
        if question.question_type == 'mcq':
            selected_choice = get_object_or_404(Choice, id=request.POST.get('choice'))
            UserResponse.objects.create(user=request.user, question=question, selected_choice=selected_choice)
            if selected_choice.is_correct:
                update_leaderboard_points(request.user, points)
        else:
            user_answer = request.POST.get('answer')
            UserResponse.objects.create(user=request.user, question=question, answer_text=user_answer)
            if user_answer.lower().strip() == question.correct_answer.lower().strip():
                update_leaderboard_points(request.user, points)

        return HttpResponseRedirect(reverse('quiz:display_question', args=[question_id]))

    leaderboard_entry = Leaderboard.objects.get_or_create(user=request.user, defaults={'points': 0})[0]
    leaderboard = Leaderboard.objects.all().order_by('-points')
    user_rank = list(leaderboard).index(leaderboard_entry) + 1

    context = {
        'question': question,
        'time_remaining': time_remaining,
        'next_question': next_question,
        'correct_answer': question.correct_answer,
        'explanation': question.explanation,
        'rank': user_rank     
        }
    return render(request, 'quiz/question.html', context)

@login_required
def leaderboard(request):
    leaderboard = Leaderboard.objects.all().order_by('-points')
    ranked_leaderboard = [{'user': entry.user, 'points': entry.points, 'rank': i + 1} for i, entry in enumerate(leaderboard)]
    user_rank = next((entry['rank'] for entry in ranked_leaderboard if entry['user'] == request.user), None)
    return render(request, 'quiz/leaderboard.html', {'leaderboard': leaderboard, 'user_rank': user_rank})

@login_required
def quiz_finished(request):
    leaderboard = Leaderboard.objects.all().order_by('-points')
    return render(request, 'quiz/finished.html', {'leaderboard': leaderboard})

def update_leaderboard_points(user, points):
    leaderboard_entry, _ = Leaderboard.objects.get_or_create(user=user, defaults={'points': 0})
    leaderboard_entry.points += points
    leaderboard_entry.save()