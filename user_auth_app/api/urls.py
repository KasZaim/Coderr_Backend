from django.urls import path
from .views import RegistrationView,CustomLoginView #UserProfileList, UserProfileDetail,,GuestLoginView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # path('profiles/', UserProfileList.as_view(), name='user-list'),
    # path('profiles/<int:pk>/', UserProfileDetail.as_view(), name='user-detail'),
    path('registration/', RegistrationView.as_view(), name='registration-detail'),
    path('login/', CustomLoginView.as_view(), name='login')
    #  path('guest-login/', GuestLoginView.as_view(), name='guest-login'),
]