import os
import uuid, csv
import re
from urllib.parse import urlparse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.encoding import force_bytes, force_text
from django.shortcuts import HttpResponse, redirect, render
from .models import *
from datetime import datetime
from django.core.mail import send_mail

def is_registration_open():
    registration_status = RegistrationsOpen.objects.first()
    return registration_status and registration_status.is_open

def home(request):
    return render(request, 'home.html')

def team(request):
    if request.user.is_authenticated and Team.objects.filter(user=request.user).first().is_leader == False:
        return redirect('/join-team')
    if request.user.is_authenticated:
        return redirect('/create-team')
    else:
        return redirect('/')

def createTeam(request):
    if request.method == "POST":
            # Registration closed
        if not is_registration_open():
            messages.warning(request, 'Registration is now closed')
            return redirect('/join-team')
        else:
            team_name = request.POST.get('team_name')
            if team_name == '':
                messages.error(request, 'Team name is required')
                return redirect('/create-team')
            update_team_name = Team.objects.filter(user=request.user).first()
            update_team_name.team_name = team_name
            update_team_name.save()
            fname1 = request.POST.get('fname-1')
            lname1 = request.POST.get('lname-1')
            email1 = request.POST.get('email-1').strip()
            phone1 = request.POST.get('phone-1')
            fname2 = request.POST.get('fname-2')
            lname2 = request.POST.get('lname-2')
            email2 = request.POST.get('email-2').strip()
            phone2 = request.POST.get('phone-2')
            fname3 = request.POST.get('fname-3')
            lname3 = request.POST.get('lname-3')
            email3 = request.POST.get('email-3').strip()
            phone3 = request.POST.get('phone-3')
            teamKey = Team.objects.filter(user=request.user).first()
            if ((email1 == '' and email2 == '' and email3 == '') or (phone1 == '' and phone2 == '' and phone3 == '')):
                messages.warning(request, 'Team deleted. Now you can join other team or create again')
                TeamMember.objects.filter(team=teamKey).all().delete()
                is_team_leader = Team.objects.filter(user=request.user).first()
                is_team_leader.is_leader = False
                is_team_leader.save()
                return redirect('/join-team')
            if ((email1 != '' and (email1 == email2 or email1 == email3)) or (email2 != '' and (email2 == email1 or email2 == email3)) or (email3 != '' and (email3 == email1 or email3 == email2)) or (email1 == teamKey.user.email or email2 == teamKey.user.email or email3 == teamKey.user.email)):
                messages.error(request, 'Email cannot be same')
                return redirect('/create-team')
            already = TeamMember.objects.filter(team=teamKey).all()
            index = 1
            for i in already:
                if len(i.email) != 0 and index == 1:
                    email1 = ''
                if len(i.email) != 0 and index == 2:
                    email2 = ''
                if len(i.email) != 0 and index == 3:
                    email3 = ''
                index += 1
            if email1 != '':
                token = str(uuid.uuid4())
                subject = f'Invitation to Join Team {team_name} - Hult Prize'
                message = f'Invitation to join {request.user.first_name} {request.user.last_name}\'s team. Click on the link to join - https://hult.edcnitd.co.in/leader-invitation/{token} \n\nWith Regards,\nTeam Entrepreneurship Development Cell (EDC NITD)'
                recipient_list = [email1]

                context = {'link':f'https://hult.edcnitd.co.in/leader-invitation/{token}','request':f'Invitation to join {request.user.first_name} {request.user.last_name}\'s team. Click on the button to join','button_name':"Join",'subject':subject}
                html_message = render_to_string('sendemail.html',context)
                plain_message = strip_tags(html_message)

                email = EmailMultiAlternatives(subject,plain_message,settings.EMAIL_HOST_USER,recipient_list)
                email.attach_alternative(html_message, 'text/html')
                email.send()
                #send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
                unverified1 = UnverifiedTeamMember(team=teamKey, first_name=fname1, last_name=lname1, email=email1, phone_no=phone1, token=token)
                unverified1.save()
            if email2 != '':
                token = str(uuid.uuid4())
                subject = f'Invitation to Join Team {team_name} - Hult Prize'
                message = f'Invitation to join {request.user.first_name} {request.user.last_name}\'s team. Click on the link to join - https://hult.edcnitd.co.in/leader-invitation/{token} \n\nWith Regards,\nTeam Entrepreneurship Development Cell (EDC NITD)'
                recipient_list = [email2]

                context = {'link':f'https://hult.edcnitd.co.in/leader-invitation/{token}','request':f'Invitation to join {request.user.first_name} {request.user.last_name}\'s team. Click on the button to join','button_name':"Join",'subject':subject}
                html_message = render_to_string('sendemail.html',context)
                plain_message = strip_tags(html_message)

                email = EmailMultiAlternatives(subject,plain_message,settings.EMAIL_HOST_USER,recipient_list)
                email.attach_alternative(html_message, 'text/html')
                email.send()
                #send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
                unverified2 = UnverifiedTeamMember(team=teamKey, first_name=fname2, last_name=lname2, email=email2, phone_no=phone2, token=token)
                unverified2.save()
            if email3 != '':
                token = str(uuid.uuid4())
                subject = f'Invitation to Join Team {team_name} - Hult Prize'
                message = f'Invitation to join {request.user.first_name} {request.user.last_name}\'s team. Click on the link to join - https://hult.edcnitd.co.in/leader-invitation/{token} \n\nWith Regards,\nTeam Entrepreneurship Development Cell (EDC NITD)'
                recipient_list = [email3]

                context = {'link':f'https://hult.edcnitd.co.in/leader-invitation/{token}','request':f'Invitation to join {request.user.first_name} {request.user.last_name}\'s team. Click on the button to join','button_name':"Join",'subject':subject}
                html_message = render_to_string('sendemail.html',context)
                plain_message = strip_tags(html_message)

                email = EmailMultiAlternatives(subject,plain_message,settings.EMAIL_HOST_USER,recipient_list)
                email.attach_alternative(html_message, 'text/html')
                email.send()
                #send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
                unverified3 = UnverifiedTeamMember(team=teamKey, first_name=fname3, last_name=lname3, email=email3, phone_no=phone3, token=token)
                unverified3.save()
            is_team_leader = Team.objects.filter(user=request.user).first()
            is_team_leader.is_leader = True
            is_team_leader.save()
            messages.success(request, 'Invitation to join has been sent to the submitted email/s')
            messages.warning(request, 'After the invitation has been accepted, it will be visible here')
            return redirect('/create-team')
    if request.user.is_authenticated:
        if not is_registration_open():
            messages.warning(request, 'Registration is now closed')
            return redirect('/join-team')
        
        team = Team.objects.filter(user=request.user).first()
        team_members = TeamMember.objects.filter(team=team).all()
        return render(request, 'create-team.html', { 'team_members': team_members, 'team': team })
    else:
        return redirect('/')
       

def leaderInvitation(request, token):
    if request.method == 'GET':
        unverified = UnverifiedTeamMember.objects.filter(token=token).first()
        if unverified is not None:
            first_name = unverified.first_name
            last_name = unverified.last_name
            team = unverified.team
            email = unverified.email
            phone_no = unverified.phone_no
            tm_count = 0
            for i in TeamMember.objects.filter(team=team).all():
                if len(i.email) != 0:
                    tm_count += 1
            if tm_count == 3:
                messages.error(request, 'Already 4 members in the team')
                return redirect('/')
            team_members = TeamMember.objects.filter(team=team).all()
            for i in team_members:
                if i.email == email:
                    unverified.delete()
                    messages.error(request, 'Email cannot be same')
                    return redirect('/')
            verified = TeamMember(team=team, first_name=first_name, last_name=last_name, email=email, phone_no=phone_no)
            verified.save()
            all_members = TeamMember.objects.filter(team=team).all()
            for member in all_members:
                if len(member.email) == 0:
                    member.delete()
            left = 3 - TeamMember.objects.filter(team=team).all().count()
            while left > 0:
                left = left - 1
                TeamMember(team=team, first_name='', last_name='', phone_no='', email='').save()
            subject = f'Invitation Accepted - Hult Prize'
            message = f'{first_name} {last_name} has successfully joined your Team {team.team_name} \n\nWith Regards,\nTeam Entrepreneurship Development Cell (EDC NITD)'
            recipient_list = [team.user.email]

            context = {'link':f'https://hult.edcnitd.co.in/login','request':f'{first_name} {last_name} has successfully joined your Team {team.team_name}. Click on the button below to login :','button_name':"Login",'subject':subject}
            html_message = render_to_string('sendemail.html',context)
            plain_message = strip_tags(html_message)

            email = EmailMultiAlternatives(subject,plain_message,settings.EMAIL_HOST_USER,recipient_list)
            email.attach_alternative(html_message, 'text/html')

            email.send()
            #send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
            unverified.delete()
            messages.success(request, 'You have successfully joined the team')
            return redirect('/')
        else:
            return redirect('/')

def handleLogin(request):
    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username=username).first()
        if user_obj is None:
            messages.error(request, 'User not found')
            return redirect('/login')
        team_obj = Team.objects.filter(user=user_obj).first()
        if not team_obj.is_verified:
            messages.info(request, 'Profile is not verified yet. Please check your mail')
            return redirect('/login')
        user = authenticate(username=username, password=password)
        if user is None:
            messages.error(request, 'Wrong password or username')
            return redirect('/login')
        login(request, user)
        if Team.objects.filter(user=request.user).first().is_leader == False:
            return redirect('/join-team')
        else:
            return redirect('/create-team')
    else:
        if request.user.is_authenticated:
            if Team.objects.filter(user=request.user).first().is_leader == False:
                return redirect('/join-team')
            else:
                return redirect('/create-team')
        else:
            return render(request, 'login.html')

def handleLogout(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, "Logged out successfully")
        return redirect('/')
    else:
        return HttpResponse("404 - Page not found")

def handleSignUp(request):
    if request.method == 'POST':
        # Registration closed
        if not is_registration_open():
            messages.warning(request, 'Registration is now closed')
            return redirect('/')
        else:
            username = request.POST.get('username')
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            phone_no = request.POST.get('phone-no')

            try:
                email_domain = email.split('@')[1]
                pattern = r"^[a-zA-Z0-9._%+-]+@([a-zA-Z0-9.-]+\.)?nitdgp\.ac\.in$"
                if not re.match(pattern, email):
                    messages.warning(request, 'Please use a valid nitdgp.ac.in email address.')
                    return redirect('/signup')
                if User.objects.filter(username=username).first():
                    messages.warning(request, 'Username is already taken')
                    return redirect('/signup')
                if User.objects.filter(email=email).first():
                    messages.warning(request, 'Email is already taken.')
                    return redirect('/signup')
                if password1 != password2:
                    messages.warning(request, 'Passwords do not match')
                    return redirect('/signup')
                user =  User.objects.create_user(username, email, password1)
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                auth_token = str(uuid.uuid4())
                team = Team(user=user, auth_token=auth_token, leader_phone_no=phone_no, is_leader=False)
                team.save()
                sendMail(email, auth_token)
                return redirect('/token')
            except Exception as e:
                messages.error(request, 'Error occured')
                return redirect('/')
    else:
        if not is_registration_open():
            messages.warning(request, 'Registration is now closed')
            return redirect('/login')
        if request.user.is_authenticated:
            return redirect('/create-team')
        else:    
            return render(request, 'signup.html')
        

def token(request):
    return render(request, 'token.html')

def sendMail(email, token):
    subject = 'Verify your account - Hult Prize'
    message = f'Please click the link to verify your account https://hult.edcnitd.co.in/verify/{token} \n\nWith Regards,\nTeam Entrepreneurship Development Cell (EDC NITD)'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    context = {
        'link': f'https://hult.edcnitd.co.in/verify/{token}',
        'request': 'Please click the link to verify your account',
        'button_name': "Verify Email",
        'subject': subject,
        'pre_registration_link': 'https://www.hultprize.org/startup-pre-registration-is-now-open/'
    }

    html_message = render_to_string('sendemail.html', context)
    plain_message = strip_tags(html_message)

    msg = EmailMultiAlternatives(subject, plain_message, email_from, recipient_list)
    msg.attach_alternative(html_message, 'text/html')
    msg.send()
    #send_mail(subject, message, None, recipient_list)

def send_registration_reminder(user):
    token = str(uuid.uuid4())
    subject = 'Reminder: Complete Your Registration for Hult Prize'
    recipient_list = [user.email]

    context = {
        'link': f'https://hult.edcnitd.co.in/join-team',
        'request': f'Dear {user.first_name}, please complete your registration for the Hult Prize. Click on the button to complete your registration.',
        'button_name': "Complete Registration",
        'subject': subject,
        'pre_registration_link': 'https://www.hultprize.org/startup-pre-registration-is-now-open/'

    }
    html_message = render_to_string('sendemail.html', context)
    plain_message = strip_tags(html_message)

    email = EmailMultiAlternatives(subject, plain_message, settings.EMAIL_HOST_USER, recipient_list)
    email.attach_alternative(html_message, 'text/html')
    email.send()

def send_reminders_to_users():
    users_to_remind = User.objects.filter(is_active=True)
    for user in users_to_remind:
        send_registration_reminder(user)

def verify(request, auth_token):
    try:
        team_obj = Team.objects.filter(auth_token=auth_token).first()
        if team_obj:
            if team_obj.is_verified:
                messages.success(request, 'Your account is already verified')
                return redirect('/')
            team_obj.is_verified = True
            team_obj.save()
            messages.success(request, 'Your account has been verified')
            return redirect('/login')
        else:
            return redirect('/error')
    except Exception as e:
        return redirect('/')

def teamsCSV(request):
    if request.user.username == 'admin':
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="teams.csv"'
        writer = csv.writer(response)
        # Team formed
        writer.writerow(
                [
                    "Team name",
                    "Team Members",
                    "Email",
                    "Phone No."
                ]
            )
        for team in Team.objects.all():
            if TeamMember.objects.filter(team=team).all().count() != 0:
                writer.writerow(
                    [
                        team.team_name,
                        team.user.first_name + " " + team.user.last_name + " " + "(Leader)",
                        team.user.email,
                        team.leader_phone_no
                    ]
                )
                team_members = TeamMember.objects.filter(team=team).all()
                for team_member in team_members:
                    writer.writerow(
                        [
                            team.team_name,
                            team_member.first_name + " " + team_member.last_name,
                            team_member.email,
                            team_member.phone_no
                        ]
                    )
                writer.writerow([])
        writer.writerow([])
        writer.writerow(["Registered but not part of a team"])
        writer.writerow([])
        # Team not formed
        writer.writerow(
                [
                    "Name",
                    "Email",
                    "Phone No."
                ]
            )
        for team in Team.objects.all():
            if TeamMember.objects.filter(team=team).all().count() == 0 and TeamMember.objects.filter(email=team.user.email).all().count() == 0:
                writer.writerow(
                    [
                        team.user.first_name + " " + team.user.last_name,
                        team.user.email,
                        team.leader_phone_no
                    ]
                )
        return response
    else:
        return redirect('/')

def faqs(request):
    faqs = Faq.objects.all()
    return render(request, 'faqs.html', { 'faqs': faqs })

def speakers(request):
    speakers = Speaker.objects.all().order_by('year').reverse()
    unique_years = Speaker.objects.values_list('year', flat=True).order_by('year').reverse().distinct()
    data = []
    for i in speakers:
        faqs = SpeakersFaq.objects.filter(speaker=i).all()
        faq = []
        for q in faqs:
            faq.append({
                'question': q.question,
                'answer': q.answer
            })
        data.append(faq)
    return render(request, 'speakers.html', { 'speakers': speakers, 'data': data , 'uniqueyears': unique_years })

def joinTeam(request):
    if request.method == 'POST':
        if not is_registration_open():
            messages.warning(request, 'Registration is now closed')
            return redirect('/join-team')
        else:
            if Team.objects.filter(user=request.user).first().is_leader == False and Team.objects.filter(user = request.user).__len__ == 1:
                auth_token = request.POST.get('auth_token')
                team = Team.objects.filter(auth_token=auth_token).first()
                team_from = Team.objects.filter(user=request.user).first()
                team_leader_email = team.user.email
                if team_from.can_request == True:
                    subject = f'Request to join your team - {request.user.first_name + " " + request.user.last_name}'
                    message = f'{request.user.first_name + " " + request.user.last_name} would like to join your team.\nClick on the link to add - https://hult.edcnitd.co.in/accept-invitation/{Team.objects.filter(user=request.user).first().auth_token} \n\nWith Regards,\nTeam Entrepreneurship Development Cell (EDC NITD)'
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = [team_leader_email]

                    context={'link':f'https://hult.edcnitd.co.in/accept-invitation/{Team.objects.filter(user=request.user).first().auth_token}','request':f'{request.user.first_name + " " + request.user.last_name} would like to join your team.\nClick on the link to add','button_name':"Accept Invite",'subject':subject}

                    html_message = render_to_string('sendemail.html',context)
                    plain_message = strip_tags(html_message)
                    email = EmailMultiAlternatives(subject,plain_message,email_from,recipient_list)
                    email.attach_alternative(html_message, 'text/html')
                    email.send()
                    #send_mail(subject, message, email_from, recipient_list)
                    team_from.can_request = False
                    team_from.can_request_timestamp = datetime.now()
                    team_from.request_sent_to = auth_token
                    team_from.save()
                    messages.success(request, 'Your request has been sent')
                    return redirect('/join-team')
                
                else:
                    team_timestamp = team_from.can_request_timestamp.date()
                    date_now = datetime.now().date()
                    delta = date_now - team_timestamp
                    if delta.days >= 1:
                        subject = f'Request to join your team - {request.user.first_name + " " + request.user.last_name}'
                        message = f'{request.user.first_name + " " + request.user.last_name} would like to join your team.\nClick on the link to add - https://hult.edcnitd.co.in/accept-invitation/{Team.objects.filter(user=request.user).first().auth_token} \n\nWith Regards,\nTeam Entrepreneurship Development Cell (EDC NITD)'
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = [team_leader_email]
                        context={'link':f'https://hult.edcnitd.co.in/accept-invitation/{Team.objects.filter(user=request.user).first().auth_token}','request':f'{request.user.first_name + " " + request.user.last_name} would like to join your team.\nClick on the link to add','button_name':"Accept Invite",'subject':subject}
                        html_message = render_to_string('sendemail.html',context)
                        plain_message = strip_tags(html_message)

                        email = EmailMultiAlternatives(subject,plain_message,email_from,recipient_list)
                        email.attach_alternative(html_message, 'text/html')
                        email.send()
                        #send_mail(subject, message, email_from, recipient_list)
                        team_from.can_request = False
                        team_from.can_request_timestamp = datetime.now()
                        team_from.save()
                        messages.success(request, 'Your request to join the team has been sent. Please wait for the leader to accept it')
                        return redirect('/join-team')
                    messages.error(request, 'Request can been sent only once in 24 hours')
                    return redirect('/join-team')
            else:
                    if Team.objects.filter(user=request.user).first().is_leader == True:
                        messages.warning(request, 'You are Team Leader so you cannot join other team. Remove all members from your team to be able join other teams')
                    else:
                        messages.warning(request, 'You are already in a team so you cannot join other team.')
                    return redirect('/join-team')
    else:
        if request.user.is_authenticated:
            teams = Team.objects.exclude(user=request.user)
            data = []
            team_from = Team.objects.filter(user=request.user).first()
            team_timestamp = team_from.can_request_timestamp.date()
            date_now = datetime.now().date()
            delta = date_now - team_timestamp
            if delta.days >= 1:
                team_from.can_request = True
                team_from.can_request_timestamp = datetime.now()
                team_from.save()
            for team in teams:
                team_member = TeamMember.objects.filter(team=team).all()
                request_sent_to = Team.objects.filter(user=request.user).first().request_sent_to
                can_request = Team.objects.filter(user=request.user).first().can_request
                if request_sent_to != '':
                    request_sent_to_team = TeamMember.objects.filter(team=Team.objects.filter(auth_token=request_sent_to).first()).all()
                    request_sent_to_team_count = 0
                    for i in request_sent_to_team:
                        if i.email != '':
                            request_sent_to_team_count += 1
                    if request_sent_to_team_count == 3:
                        can_request = True
                        team_from.can_request = True
                        team_from.can_request_timestamp = datetime.now()
                        team_from.request_sent_to = ''
                        team_from.save()
                if team_member.count() != 0:
                    no_of_members = 0
                    for tm in team_member:
                        if tm.email != '':
                            no_of_members += 1
                    data.append({
                        'team_name':team.team_name,
                        'leader': team.user.first_name + " " + team.user.last_name,
                        'auth_token': team.auth_token,
                        'team_member': team_member,
                        'is_leader': Team.objects.filter(user=request.user).first().is_leader,
                        'can_request': can_request,
                        'no_of_members': no_of_members
                    })
            return render(request, 'join-team.html', { 'data': data })
        else:
            return redirect('/')

def myTeam(request):
    if request.user.is_authenticated:
        myData = TeamMember.objects.filter(email=request.user.email).first()
        if myData is None:
            myData = Team.objects.filter(user=request.user).first()
            team_data = TeamMember.objects.filter(team=myData)
            team_name = myData.team_name
            team_leader = myData.user.first_name + " " + myData.user.last_name
            data = []
            data.append({
                'team_name': team_name,
                'team_leader': team_leader,
                'team_members': team_data
            })
        else:
            team_data = TeamMember.objects.filter(team=myData.team)
            team_leader = myData.team.user.first_name + " " + myData.team.user.last_name
            team_name = myData.team.team_name
            data = []
            data.append({
                'team_name': team_name,
                'team_leader': team_leader,
                'team_members': team_data
            })
        return render(request, 'my-team.html', { 'my_team': data })
    else:
        return redirect('/')

def acceptInvitation(request, auth_token):
    if request.user.is_authenticated:
        data = Team.objects.filter(auth_token=auth_token).first()
        team = Team.objects.filter(user=request.user).first()
        c = 0
        for i in TeamMember.objects.filter(team=team):
            if len(i.email) != 0:
                c = c + 1
        if c < 3:
            TeamMember(team=team, first_name=data.user.first_name, last_name=data.user.last_name, phone_no=data.leader_phone_no, email=data.user.email).save()
            for i in TeamMember.objects.filter(team=team):
                if len(i.email) == 0:
                    i.delete()
            left = 3 - TeamMember.objects.filter(team=team).count()
            while left > 0:
                left = left - 1
                TeamMember(team=team, first_name='', last_name='', phone_no='', email='').save()
            team.is_leader = True
            team.save()
            subject = 'Request accepted - Hult Prize'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [Team.objects.filter(auth_token=auth_token).first().user.email]
            context = {'link':f'https://hult.edcnitd.co.in/login','request':f'Your request to join the team, {Team.objects.filter(user=request.user).first().team_name}, has been accepted. Click on the button below to login :','button_name':"Login",'subject':subject}
            html_message = render_to_string('sendemail.html',context)
            plain_message = strip_tags(html_message)

            email = EmailMultiAlternatives(subject,plain_message,email_from,recipient_list)
            email.attach_alternative(html_message, 'text/html')
            email.send()
            # send_mail(subject, message, email_from, recipient_list)
            messages.success(request, 'Member added successfully')
            return redirect('/create-team')
        else:
            messages.error(request, '4 Membes already in the team')
            return redirect('/create-team')
    else:
        messages.error(request, 'Please login first to add team member')
        return redirect('/login')
    
def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email = email)
        except User.DoesNotExist:
            messages.error(request,' No user found with this email.')
            return redirect('request_password_reset')
        
        #token and url generation
        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        link = request.build_absolute_uri(f'/request-password-reset/confirm/{uidb64}/{token}/')

        #sending email
        subject = 'Reset Password - Hult Prize'
        context = {'link': link,'request':"You have requested to reset your password. Click the button below to proceed:",'button_name':"Reset Password",'subject':subject}
        html_message = render_to_string('sendemail.html', context)
        plain_message = strip_tags(html_message)
        
        email = EmailMultiAlternatives(subject, plain_message, settings.EMAIL_HOST_USER, [email])
        email.attach_alternative(html_message, 'text/html')
        email.send()

        return redirect('reset-token')

    return render(request,'forgotpassword.html')

def resettoken(request):
    return render(request, 'reset-token.html')

def reset_password_confirm(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            if password1 == password2:
                user.set_password(password1)
                user.save()
                messages.success(request,'Password Updated')
            else:
                messages.warning(request, 'Passwords do not match')
                return render(request, 'password_reset.html')
            return redirect('/login')
        return render(request, 'password_reset.html')
    else:
        messages.error(request, 'Password reset link is invalid.')
        return redirect('request_password_reset')