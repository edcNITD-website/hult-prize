from django.db import models
import uuid
from django.contrib.auth.models import User
from django.utils.timezone import now
class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4())
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Category(BaseModel):
    category_name = models.CharField(max_length=255)
class Question(BaseModel):

    TEXT = 'text'
    MCQ = 'mcq'

    QUESTION_TYPE_CHOICES = [
        (TEXT, 'Text Input'),
        (MCQ, 'Multiple Choice'),
    ]
    
    category=models.ForeignKey(Category,related_name='category',on_delete=models.CASCADE)
    question_text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPE_CHOICES)
    marks = models.IntegerField(default=10)
    correct_answer = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.question_text

class Choice(BaseModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text

# User Response Model
class UserResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True, null=True)  # For text-based answers
    selected_choice = models.ForeignKey(Choice, blank=True, null=True, on_delete=models.CASCADE)  # For MCQ
    submission_time = models.DateTimeField(default=now)  # Capture when user submitted answer

    def __str__(self):
        return f'{self.user} - {self.question}'

# Leaderboard Model
class Leaderboard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # One entry per user
    points = models.IntegerField(default=0)  # Default points set to 0

    def __str__(self):
        return f'{self.user.username}: {self.points} points'
