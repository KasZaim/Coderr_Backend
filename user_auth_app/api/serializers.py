#api/serializer.py
from rest_framework import serializers
from user_auth_app.models import UserProfile
from django.contrib.auth.models import User
from ...coderr_app.models import UserProfile

class UserSerializer(serializers.HyperlinkedModelSerializer):
    profile = UserProfile(source='userprofile', read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='user-detail', lookup_field='pk')
    class Meta:
        model = User
        fields = ['username', 'email','first_name', 'last_name', 'profile', 'url']

        
        
class RegistrationSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'profile']  #'repeated_password'
        extra_kwargs= {
            'password':{
                'write_only': True
            }
        }
        
    def save(self):
        email = self.validated_data['email']
        pw = self.validated_data['password']
        profile_data = self.validated_data.pop('profile')
        first_name=self.validated_data.get('first_name') 
        last_name=self.validated_data.get('last_name', '')
        # repeated_pw = self.validated_data['repeated_password']
        
        if User.objects.filter(email=email).exists():
           raise serializers.ValidationError({'email': 'A user with this email already exists.'})
        
        # if pw != repeated_pw:
        #     raise serializers.ValidationError({'error':'passwords dont match'})
        
        account = User(email=email,username=self.validated_data['username'], first_name=first_name, last_name=last_name)
        account.set_password(pw)
        account.save()
        UserProfile.objects.create(user=account, **profile_data)
        return account