from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path, re_path
from django.views.generic import RedirectView

from accountapp.views import AccountCreateAPI
from accountapp.views import ActivateAccountAPI
from accountapp.views import LoginAPI, LogoutAPI, UserProfileUpdateAPI, UserProfileDetailAPI, PasswordResetRequestAPI, UsernameRecoveryAPI, AccountDeleteAPI, ChangePasswordAPI

app_name = 'account'

urlpatterns = [
    path('signup/', AccountCreateAPI.as_view(), name='signup'),
    path('activate/<uidb64>/<token>/', ActivateAccountAPI.as_view(), name='activate'),
    path('login/', LoginAPI.as_view(), name='login'),
    path('logout/', LogoutAPI.as_view(), name='logout'),
    path('profile/<slug:slug>/', UserProfileDetailAPI.as_view(), name='profile_detail'),
    path('profile/<slug:slug>/update/', UserProfileUpdateAPI.as_view(), name='profile_update'),
    re_path(r'^pwreset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', RedirectView.as_view(url='http://localhost:3000/password-reset/%(uidb64)s/%(token)s')),
    #path('pwreset/<uidb64>/<token>/', PasswordResetConfirmAPI.as_view(), name='password_reset_confirm'),
    path('pwreset-request/', PasswordResetRequestAPI.as_view(), name='password_reset_request'),
    path('recover-username/', UsernameRecoveryAPI.as_view(), name='recover_username'),
    path('delete-account/', AccountDeleteAPI.as_view(), name='delete_account'),
    path('pw-change/', ChangePasswordAPI.as_view(), name='pw_change'),
]