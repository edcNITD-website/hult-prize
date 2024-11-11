from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class RegistrationsOpen(models.Model):
    is_open = models.BooleanField(default=False)

    def __str__(self):
        return "Registrations Open: " + str(self.is_open)
    
class Team(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    auth_token = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    team_name = models.CharField(max_length=100)
    leader_phone_no = models.CharField(max_length=10)
    can_request = models.BooleanField(default=True)
    can_request_timestamp = models.DateTimeField(auto_now_add=True, blank=True)
    request_sent_to = models.CharField(blank=True, max_length=120)
    is_leader = models.BooleanField(default=False, blank=True)
    def __str__(self):
        return self.user.username + " | " + self.team_name

class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_no = models.CharField(max_length=10)
    email = models.EmailField()
    def __str__(self):
        return self.team.team_name + " - " + self.first_name + " " + self.last_name

class Faq(models.Model):
    question = models.CharField(max_length=200)
    answer = models.TextField()
    def __str__(self):
        return "FAQ | " + self.question

class Speaker(models.Model):
    name = models.CharField(max_length=200)
    about = models.TextField()
    photo = models.FileField(upload_to='speakers/')
    year = models.IntegerField(
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(2100)
        ],blank=True)
    def __str__(self):
        return "Speaker | " + self.name

class UnverifiedTeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_no = models.CharField(max_length=10)
    email = models.EmailField()
    token = models.CharField(max_length=100)
    def __str__(self):
        return self.team.team_name + " - " + self.first_name + " " + self.last_name

class SpeakersFaq(models.Model):
    speaker = models.ForeignKey(Speaker, on_delete=models.CASCADE)
    question = models.CharField(max_length=200)
    answer = models.TextField()
    def __str__(self):
        return self.speaker.name + " | " + self.question
