from django.urls import reverse
from rest_framework import serializers
from ..models import UserProfile, Offers, OfferDetails,Order
from django.conf import settings


class UserProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
    source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'location',
            'email',
            'file',
            'description',
            'tel',
            'working_hours',
            'type',
            'created_at']

        read_only_fields = ['user', 'created_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.file:
            representation['file'] = f"{settings.MEDIA_URL}{instance.file.name}"

        return representation


class UserProfileDetailSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    class Meta:
        model = UserProfile
        fields = [
            'user',
            'file',
            'location',
            'tel',
            'description',
            'working_hours',
            'type'
        ]
        read_only_fields = ['id', 'type', 'created_at']
        
    def get_user(self, obj):
        """
        Generiert die verschachtelte Struktur für das 'user'-Feld.
        """
        user = obj.user
        return {
            "pk": user.pk,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }

class CustomerProfileSerializer(UserProfileDetailSerializer):
    
    class Meta:
        model = UserProfile
        fields = [
            'user',         
            'file',        
            'created_at', 
            'type'          
        ]
        read_only_fields = ['type']


class OfferDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = OfferDetails
        fields = [
            'id',
            'title',
            'price',
            'offer',
            'delivery_time_in_days',
            'revisions',
            'additional_information',
            'features',
            'offer',
            'offer_type'
        ]
        read_only_fields = ['id', 'offer']


class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailsSerializer(many=True)
    min_delivery_time = serializers.IntegerField(read_only=True)
    max_delivery_time = serializers.IntegerField(read_only=True)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offers
        fields = [
            'id',
            'title',
            'min_delivery_time',
            'max_delivery_time',
            'min_price',
            'user',
            'user_details',
            'image',
            'description',
            'details',  # Details werden hier eingebunden
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_user_details(self, obj):
        user = obj.user
        return {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
        }

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        user = self.context['request'].user
        offer = Offers.objects.create(user=user, **validated_data)

        for detail in details_data:
            print("Detail before creation:", detail)
            OfferDetails.objects.create(offer=offer, **detail)
        return offer
    
    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        if details_data:
            instance.details.all().delete()

            for detail in details_data:
                OfferDetails.objects.create(offer=instance, **detail)
        return instance


class OrderSerializer(serializers.ModelSerializer):
    offer_detail_id = serializers.IntegerField(write_only=True)
    business_user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Order
        fields = [
            'id',
            'status',
            'business_user',
            'customer_user',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
            'created_at',
            'updated_at',
            'offer_detail_id',
        ]
        read_only_fields = [
            'id',
            'business_user',
            'customer_user',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
            'created_at',
            'updated_at',
        ]

    def create(self, validated_data):
        offer_detail_id = validated_data.pop('offer_detail_id')
        offer_detail = OfferDetails.objects.get(id=offer_detail_id)
        
        
        offer = offer_detail.offer
        business_user = offer.user
        customer_user = self.context['request'].user
        print(offer, business_user)
        order = Order.objects.create(
            customer_user=customer_user,
            business_user=business_user,
            offer=offer,
            offer_detail=offer_detail,
            status='pending',
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
        )
        return order
