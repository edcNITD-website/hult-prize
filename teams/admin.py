from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register((RegistrationsOpen,Team, TeamMember, Faq, Speaker, UnverifiedTeamMember, SpeakersFaq))
