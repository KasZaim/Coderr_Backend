from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .serializers import RegistrationSerializer
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.contrib.auth.models import User
from rest_framework import status

class RegistrationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegistrationSerializer(data = request.data)
        data = {}
        
        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account)
            data = {
                'token': token.key,
                'username': saved_account.username,
                'email': saved_account.email,
                'user_id':saved_account.id
                
            }
        else:
            data=serializer.errors
            
        return Response(data)
    
class CustomLoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = AuthTokenSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data = request.data)
        data = {}
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            data = {
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'user_id': user.id
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Email or Password are invalid"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
# class GuestLoginView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         try:
#             guest_user = User.objects.get(username="guest_user")
#         except User.DoesNotExist:
#             guest_user = User.objects.create_user(username="guest_user", password="guest_password")
        
#         token, created = Token.objects.get_or_create(user=guest_user)
#         return Response({
#             'token': token.key,
#             'username': guest_user.username
#         }, status=status.HTTP_200_OK)