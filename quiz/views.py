from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from datetime import datetime, timedelta
import pytz

IST = pytz.timezone('Asia/Kolkata')
QUIZ_START_TIME = IST.localize(datetime(2024, 11, 2, 19, 5, 0)) 
QUIZ_END_TIME = IST.localize(datetime(2024, 11, 2, 19, 36, 0)) # Set Time for the Quiz 
QUESTION_DURATION = 90  # Set question duration in seconds
MAX_POINTS = 100  # Set the Points

def quiz_home(request):
    return render(request, 'quiz/quiz_home.html')

def get_next_question(user):
    answered_questions = UserResponse.objects.filter(user=user).values_list('question', flat=True)
    questions = Question.objects.all().order_by('id').exclude(id__in=answered_questions)

    if not questions:
        return None
    
    return questions[0] 

@login_required
def start_quiz(request):
    current_time = timezone.now()
    quiz_title = "Quiz"
    quiz_start_time = QUIZ_START_TIME.strftime("%Y-%m-%d %H:%M:%S")

    if current_time < QUIZ_START_TIME:
        return render(request, 'quiz/not_started.html', {
            'quiz': {
                'title': quiz_title,
                'start_time': quiz_start_time,
            }
        })

    first_question = get_next_question(request.user)
    if QUIZ_END_TIME < current_time or not first_question:
        return redirect('quiz_finished')
    if first_question:
        return redirect('quiz:display_question', question_id=first_question.id)
    else:
        return redirect('quiz_finished')
    
@login_required
def display_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    questions = Question.objects.all().order_by('id')
    question_index = list(questions).index(question)

    question_start_time = QUIZ_START_TIME + timedelta(seconds=QUESTION_DURATION * question_index)
    time_remaining = max(0, QUESTION_DURATION - int((timezone.now() - question_start_time).total_seconds()))
    
    next_question = questions[question_index + 1] if question_index + 1 < len(questions) else None

    time_is_up = (time_remaining == 0)
    if time_is_up:
        if next_question:
            return redirect('quiz:display_question', question_id=next_question.id)
        else:
            return redirect('quiz_finished')

    if request.method == 'POST' and not UserResponse.objects.filter(user=request.user, question=question).exists():
        points = max(0, int((time_remaining / QUESTION_DURATION) * MAX_POINTS))

        if question.question_type == 'mcq':
            selected_choice = get_object_or_404(Choice, id=request.POST.get('choice'))
            UserResponse.objects.create(user=request.user, question=question, selected_choice=selected_choice)
            if selected_choice.is_correct:
                update_leaderboard_points(request.user, points)
        else:
            user_answer = request.POST.get('answer')
            UserResponse.objects.create(user=request.user, question=question, answer_text=user_answer)
            if user_answer.lower().replace(" ", "") == question.correct_answer.lower().replace(" ", ""):
                update_leaderboard_points(request.user, points)

    next_question = questions[question_index + 1] if question_index + 1 < len(questions) else None


    leaderboard_entry = Leaderboard.objects.filter(user=request.user).first()

    if leaderboard_entry is None:
        leaderboard_entry = Leaderboard.objects.create(user=request.user, points=0)

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


# @login_required
def leaderboard(request):
    leaderboard = Leaderboard.objects.all().order_by('-points')
    ranked_leaderboard = [
        {'user': entry.user, 'points': entry.points, 'rank': i + 1}
        for i, entry in enumerate(leaderboard)
    ]
    current_user_entry = next((entry for entry in ranked_leaderboard if entry['user'] == request.user), None)
    user_rank = current_user_entry['rank'] if current_user_entry else None
    return render(request, 'quiz/leaderboard.html', {'leaderboard': leaderboard})

@login_required
def quiz_finished(request):
    leaderboard = Leaderboard.objects.all().order_by('-points')
    return render(request, 'quiz/finished.html', {'leaderboard': leaderboard})

def update_leaderboard_points(user, points):
    leaderboard_entry, created = Leaderboard.objects.get_or_create(user=user, defaults={'points': 0})
    leaderboard_entry.points += points
    leaderboard_entry.save()