from django.urls import reverse
from rest_framework import serializers
from ..models import UserProfile,Offers,OfferDetails
from django.conf import settings

class UserProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['user', 'username', 'first_name', 'last_name','location', 'email', 'file', 'description', 'tel', 'working_hours', 'type', 'created_at']
        read_only_fields = ['user', 'created_at']  

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        if instance.file:
            representation['file'] = f"{settings.MEDIA_URL}{instance.file.name}"
        
        return representation
    
    
class UserProfileDetailSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id',           # Primärschlüssel des Profils
            'username',     # Benutzername des verknüpften Users
            'first_name',   # Vorname des Users
            'last_name',    # Nachname des Users
            'email',        # E-Mail-Adresse des Users
            'location',     # Standort des Profils
            'description',  # Beschreibung
            'tel',          # Telefonnummer
            'working_hours', # Arbeitszeiten
            'type',         # Typ des Profils (z. B. business, customer)
            'created_at'    # Erstellungsdatum
        ]
    read_only_fields = ['id', 'type', 'created_at']
    
    
class OfferDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetails
        fields = [
            'id', 
            'offer',  # Verknüpfung zum Angebot
            'delivery_time_in_days', 
            'revisions', 
            'additional_information',
            'features', 
            'offer_type'
        ]
    read_only_fields = ['id']
    
    
class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailsSerializer(many=True, read_only=True)

    class Meta:
        model = Offers
        fields = [
            'id',
            'title',
            'image',
            'description',
            'details',  # Details werden hier eingebunden
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']