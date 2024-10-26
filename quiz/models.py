from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from jsonfield import JSONField  # JSON field for crossword grids and clues

# Question Model
class Question(models.Model):
    TEXT = 'text'
    MCQ = 'mcq'
    CROSSWORD = 'crossword'

    QUESTION_TYPE_CHOICES = [
        (TEXT, 'Text Input'),
        (MCQ, 'Multiple Choice'),
        (CROSSWORD, 'Crossword')
    ]

    question_text = models.TextField()  # Question prompt
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPE_CHOICES)
    correct_answer = models.TextField(blank=True, null=True)  # Store correct answer (for MCQ or Text)

    def __str__(self):
        return self.question_text

# Crossword Model
class Crossword(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='crossword')
    grid = JSONField()  # JSONField for storing crossword grid
    across_clues = JSONField()  # JSONField for across clues
    down_clues = JSONField()  # JSONField for down clues
    solution = JSONField()  # Store the correct solution as a JSON map of coordinates to letters

    def __str__(self):
        return f"Crossword for Question: {self.question.id}"

# MCQ Choice Model
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)  # Identify correct option

    def __str__(self):
        return self.choice_text

# User Response Model
class UserResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True, null=True)  # For text-based answers
    selected_choice = models.ForeignKey(Choice, blank=True, null=True, on_delete=models.CASCADE)  # For MCQ
    crossword_solution = JSONField(blank=True, null=True)  # Store user’s crossword solution as a JSON object
    submission_time = models.DateTimeField(default=now)  # Capture when user submitted answer

    def __str__(self):
        return f'{self.user} - {self.question}'

# Leaderboard Model
class Leaderboard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # One entry per user
    points = models.IntegerField(default=0)  # Default points set to 0

    def __str__(self):
        return f'{self.user.username}: {self.points} points'
