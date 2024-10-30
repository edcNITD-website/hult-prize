from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from .models import Question, UserResponse, Choice, Leaderboard
import json
from datetime import datetime, timedelta

MAX_POINTS = 10  # Maximum points for a question
QUESTION_DURATION_MS = 10 * 60 * 1000  # 10 minutes in milliseconds

# Home page for quiz
def quiz_home(request):
    return render(request, 'quiz/quiz_home.html')

# Function to get the next unanswered question for the user
#def get_next_question(user, start_time):
#     # Calculate how many questions have passed based on elapsed time
#     questions_passed = (now() - start_time) // timedelta(milliseconds=QUESTION_DURATION_MS)
#     answered_questions = UserResponse.objects.filter(user=user).values_list('question', flat=True)
#     questions = Question.objects.all().order_by('id').exclude(id__in=answered_questions)  # Unanswered questions
#     return questions[questions_passed:].first()  # Return next available question

# # Start the quiz
# @login_required
# def start_quiz(request):
#     # Store the quiz start time in the session for this user
#     request.session['quiz_start_time'] = now().isoformat()
#     next_question = get_next_question(request.user, now())  # Use current time for the first question
#     if not next_question:
#         return redirect('quiz_finished')
#     return redirect('display_question', question_id=next_question.id)

# # Display a question and handle responses
# @login_required
# def display_question(request, question_id):
#     question = get_object_or_404(Question, id=question_id)

#     # Retrieve start time from session or set it to the current time if not found
#     start_time_str = request.session.get('quiz_start_time')
#     start_time = datetime.fromisoformat(start_time_str) if start_time_str else now()

#     # Calculate elapsed time since start and determine questions passed
#     time_since_start = now() - start_time
#     questions_passed = time_since_start // timedelta(milliseconds=QUESTION_DURATION_MS)

#     # Check if the question has passed based on elapsed time
#     question_position = list(Question.objects.all().order_by('id')).index(question)
#     if question_position < questions_passed:
#         return redirect('quiz_finished')

#     if request.method == 'POST':
#         time_answered = now()  # Time when the user submits the answer
#         time_elapsed = (time_answered - start_time).total_seconds() * 1000  # Convert to milliseconds
#         time_left = max(QUESTION_DURATION_MS - time_elapsed, 0)  # Ensure no negative times
#         points_earned = MAX_POINTS * (time_left / QUESTION_DURATION_MS)

#         # Handle responses for each question type
#         if question.question_type == 'mcq':
#             selected_choice = get_object_or_404(Choice, id=request.POST.get('choice'))
#             UserResponse.objects.create(user=request.user, question=question, selected_choice=selected_choice, submission_time=time_answered)
#             if selected_choice.is_correct:
#                 update_leaderboard_points(request.user, points_earned)
#         elif question.question_type == 'crossword':
#             user_solution = json.loads(request.POST.get('crossword_solution'))
#             UserResponse.objects.create(user=request.user, question=question, crossword_solution=user_solution, submission_time=time_answered)
#             # Compare user solution with the correct solution stored in the crossword
#             if user_solution == question.crossword.solution:
#                 update_leaderboard_points(request.user, points_earned)
#         else:
#             user_answer = request.POST.get('answer')
#             UserResponse.objects.create(user=request.user, question=question, answer_text=user_answer, submission_time=time_answered)
#             if user_answer == question.correct_answer:
#                 update_leaderboard_points(request.user, points_earned)

#         # Get the next question
#         next_question = get_next_question(request.user, start_time)
#         if next_question:
#             return redirect('display_question', question_id=next_question.id)
#         else:
#             return redirect('quiz_finished')

#     # Render the appropriate template based on question type
#     if question.question_type == 'crossword':
#         crossword = question.crossword
#         context = {
#             'question': question,
#             'grid': crossword.grid,
#             'across_clues': crossword.across_clues,
#             'down_clues': crossword.down_clues,
#             'leaderboard': Leaderboard.objects.all().order_by('-points'),
#         }
#         return render(request, 'quiz/crossword.html', context)

#     context = {
#         'question': question,
#         'leaderboard': Leaderboard.objects.all().order_by('-points')
#     }
#     return render(request, 'quiz/question.html', context)

# # Display the leaderboard after quiz completion
# @login_required
# def quiz_finished(request):
#     leaderboard = Leaderboard.objects.all().order_by('-points')
#     return render(request, 'quiz/finished.html', {'leaderboard': leaderboard})

# # Update leaderboard points based on how fast the user answered
# def update_leaderboard_points(user, points):
#     leaderboard_entry, created = Leaderboard.objects.get_or_create(user=user)
#     leaderboard_entry.points += points
#     leaderboard_entry.save()