# user_auth_app/api/views.py
from rest_framework import permissions
from rest_framework.generics import RetrieveUpdateAPIView
from .serializer import UserProfileSerializer
from ..models import UserProfile

class UserProfileDetailView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)
