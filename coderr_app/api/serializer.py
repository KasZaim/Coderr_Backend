from django.urls import reverse
from rest_framework import serializers
from ..models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='pk')
    class Meta:
        model = UserProfile
        fields = ['id','user', 'location', 'email', 'file', 'description', 'tel', 'working_hours', 'type', 'created_at']
        read_only_fields = ['user', 'created_at']  

    def to_representation(self, instance):
        # Ruft die Standarddarstellung ab
        representation = super().to_representation(instance)
        
        # Fügt die URL zur Detailansicht hinzu
        representation['url'] = reverse('user_profile_detail', kwargs={'pk': instance.pk})
        
        return representation