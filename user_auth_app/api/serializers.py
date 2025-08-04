from rest_framework import serializers
from coderr_app.models import UserProfile
from django.contrib.auth.models import User

class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.CharField(write_only=True)
    user_id = serializers.ReadOnlyField(source='pk')
    
    class Meta:
        model = User
        fields = ['user_id','username', 'email', 'password','repeated_password','type']  
        extra_kwargs= {
            'password':{
                'write_only': True
            }
        }
    
    def validate_user(value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value
    
    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError({'error': 'Passwords do not match.'})
        
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'A user with this email already exists.'})
        
        return data

    def save(self):
        email = self.validated_data['email']
        pw = self.validated_data['password']
        type = self.validated_data.pop('type')
               
        account = User(email=email,username=self.validated_data['username']) 
        account.set_password(pw)
        account.save()

        UserProfile.objects.create(user=account,email=email,type=type)
        return account