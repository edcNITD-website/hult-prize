from django.contrib import admin
from django.urls import path, include
from teams import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name="home"),
    path('create-team', views.createTeam, name="createTeam"),
    path('join-team', views.joinTeam, name="joinTeam"),
    path('my-team', views.myTeam, name="myTeam"),
    path('team', views.team, name="team"),
    path('accept-invitation/<auth_token>', views.acceptInvitation, name="acceptInvitation"),
    path('leader-invitation/<token>', views.leaderInvitation, name="leaderInvitation"),
    path('login', views.handleLogin, name="handleLogin"),
    path('signup', views.handleSignUp, name="handleSignUp"),
    path('logout', views.handleLogout, name="handleLogout"),
    path('token', views.token, name="token"),
    path('faqs', views.faqs, name="faqs"),
    path('speakers', views.speakers, name="speakers"),
    path('teamsCSV', views.teamsCSV, name="teamsCSV"),
    path('verify/<auth_token>', views.verify, name="verify"),
    path('request-password-reset',views.forgotPassword,name="request_password_reset"),
    path('request-password-reset/confirm/<uidb64>/<token>/',views.reset_password_confirm,name="confirm_password_reset"),
    path('reset-token', views.resettoken, name="reset-token"),
    path('quiz/', include('quiz.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
