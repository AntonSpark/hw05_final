from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeDoneView, PasswordChangeView,
    PasswordResetCompleteView, PasswordResetConfirmView, PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import path

from . import views

app_name = 'users'

temp_p_r_form = 'users/password_reset_form.html'
temp_p_r_complete = 'users/password_reset_complete.html'
temp_p_r_confirm = 'users/password_reset_confirm.html'
temp_p_r_done = 'users/password_reset_done.html'
temp_p_c_done = 'users/password_change_done.html'
temp_p_c_form = 'users/password_change_form.html'

urlpatterns = [
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),

    path(
        'signup/',
        views.SignUp.as_view(),
        name='signup'
    ),

    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),

    path(
        'password_reset/',
        PasswordResetView.as_view(template_name=temp_p_r_form),
        name='password_reset'
    ),

    path(
        'password_change/',
        PasswordChangeView.as_view(template_name=temp_p_c_form),
        name='password_change'
    ),

    path(
        'password_change/done/',
        PasswordChangeDoneView.as_view(template_name=temp_p_c_done),
        name='password_change_done'
    ),

    path(
        'password_reset/done/',
        PasswordResetDoneView.as_view(template_name=temp_p_r_done),
        name='password_reset_done'
    ),

    path(
        'reset/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(template_name=temp_p_r_confirm),
        name='password_reset_confirm'
    ),

    path(
        'reset/done/',
        PasswordResetCompleteView.as_view(template_name=temp_p_r_complete),
        name='password_reset_complete'
    ),
]
