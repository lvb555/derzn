from django.urls import path
from profiles.views import LoginFormView, RegistrationFormView, \
    LogoutFormView, ProfileTemplateView, ProfileFormView, ProfileVerifyView, \
    ProfilePasswordRecoveryFormView, ProfileSetPasswordFormView

app_name = 'profiles'

urlpatterns = [
    path('login/', LoginFormView.as_view(), name='login'),
    path('register/', RegistrationFormView.as_view(), name='register'),
    path('profile/', ProfileFormView.as_view(), name='myprofile'),
    path('<int:id>/', ProfileTemplateView.as_view(), name='usersprofile'),
    path('logout/', LogoutFormView.as_view(), name='logout'),
    path('verify/<str:username>/<str:activation_key>/',
         ProfileVerifyView.as_view(), name='verify'),
    path('password-recovery/', ProfilePasswordRecoveryFormView.as_view(),
         name='password-recovery'),
    path('password-recovery-link/<str:email>/<str:password_recovery_key>/',
         ProfileSetPasswordFormView.as_view(), name='password-recovery-link'),
]
