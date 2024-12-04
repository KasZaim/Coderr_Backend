from rest_framework import serializers
from ..models import UserProfile, Offers, OfferDetails,Order,Review
from django.conf import settings
import re


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer für das UserProfile-Modell.

    Fügt zusätzliche Felder aus dem User-Modell hinzu, wie `username`, `first_name` und `last_name`. Beinhaltet auch Profilinformationen wie Standort, E-Mail und Beschreibung.

    Meta:
    model: UserProfile
    fields: Alle oben genannten Felder.
    read_only_fields: ['user', 'created_at']
    """
   
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
    """
    Serializer für detaillierte Benutzerprofile.

    Erweitert das UserProfile um verschachtelte Benutzerinformationen und zusätzliche Profildetails.

    Meta:
    model: UserProfile
    fields: ['user', 'file', 'location', 'tel', 'description', 'working_hours', 'type']
    read_only_fields: ['id', 'type', 'created_at']

    Methoden:
    get_user(self, obj): Generiert die verschachtelte Struktur für das 'user'-Feld.
    """

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
    """
    Serializer für Kundenprofile.

    Basierend auf dem UserProfileDetailSerializer, aber spezialisiert für Kunden, mit einer reduzierten Anzahl von Feldern.
    
    Meta:
    model: UserProfile
    fields: ['user','pk', 'file', 'uploaded_at', 'type']
    read_only_fields: ['type']
    """
    uploaded_at = serializers.DateTimeField(source='created_at', read_only=True)
    class Meta:
        model = UserProfile
        fields = [
            'user',
            'pk',     
            'file',     
            'uploaded_at', 
            'type'          
        ]
        read_only_fields = ['type']


class BusinesProfileSerializer(UserProfileDetailSerializer):
    """
    Serializer für Anbieter Profile.

    Basierend auf dem UserProfileDetailSerializer, aber spezialisiert für Anbieter, mit einer reduzierten Anzahl von Feldern.
    
    Meta:
    model: UserProfile
    fields: ['user','pk', 'file','location','tel','description','working_hours', 'type']
    read_only_fields: ['type']
    """
    class Meta:
        model = UserProfile
        fields = [
            'user',
            'pk',     
            'file',
            'location',
            'tel',
            'description',
            'working_hours', 
            'type'          
        ]
        read_only_fields = ['type']
    def validate_tel(self, value):
        """
        Validiert das Telefonformat.
        Erwartetes Format: +49 123 456789 oder ähnliche internationale Formate.
        """
        phone_regex = re.compile(r'^\+?[\d\s\-()]{7,15}$')  # Erlaubt internationale Nummern
        if value and not phone_regex.match(value):
            raise serializers.ValidationError("Invalid phone number format. Example: +49 123 456789")
        return value

class OfferDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer für das OfferDetails-Modell.

    Verarbeitet die Details eines Angebots, einschließlich Preis, Lieferzeit und spezifische Merkmale.
    
    Meta:
    model: OfferDetails
    fields: Alle oben genannten Felder.
    read_only_fields: ['id', 'offer']
    """
    price = serializers.FloatField()
    class Meta:
        model = OfferDetails
        fields = [
            'id',
            'title',
            'price',
            'delivery_time_in_days',
            'revisions',
            'features',
            'offer_type'
        ]
        read_only_fields = ['id', 'offer']


class OfferSerializer(serializers.ModelSerializer):
    """
    Serializer für das Offers-Modell.

    Verarbeitet Angebote und deren Details, einschließlich Benutzerinformationen und Preis-/Lieferzeitberechnungen.

    Meta:
    model: Offers
    fields: Alle oben genannten Felder.
    read_only_fields: ['id', 'created_at', 'updated_at']

    """

    details = serializers.SerializerMethodField()
    # min_delivery_time = serializers.ReadOnlyField()
    # min_price = serializers.ReadOnlyField()
    # user = serializers.PrimaryKeyRelatedField(read_only=True)
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offers
        fields = [
            'id',
            'title',
            'image',
            'description',
            'created_at',
            'updated_at',
            'details',
            'min_price',
            'min_delivery_time',
            'user',
            'user_details',
        ]
        
        read_only_fields = ['id', 'created_at', 'updated_at','user','min_price','min_delivery_time', ]
        
    def get_details(self, obj):
        """
        Dynamische Darstellung der Angebotsdetails:
        - Für GET: Nur `id` und `url`.
        - Für POST: Detaillierte Felder.
        """
        request = self.context.get('request')

        if request and request.method == 'GET':
            return [
                {
                    'id': detail.id,
                    'url': f"/api/offerdetails/{detail.id}/"
                }
                for detail in obj.details.all()
            ]
        elif request and request.method == 'POST':
            details_serializer = OfferDetailsSerializer(obj.details.all(), many=True)
            return details_serializer.data
        return []
    
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
    """
    Serializer für das Order-Modell.

    Verarbeitet Bestellungen, die auf Angebotsdetails basieren, und stellt sicher, dass relevante Felder korrekt gesetzt werden.

    Meta:
    model: Order
    fields: Alle oben genannten Felder.
    read_only_fields: [
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

    Methoden:
    create(self, validated_data): Erstellt eine neue Bestellung basierend auf dem angegebenen Angebotsdetail und setzt die erforderlichen Felder.
    """

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
        
        order = Order.objects.create(
            customer_user=customer_user,
            business_user=business_user,
            offer=offer,
            offer_detail=offer_detail,
            status='in_progress',
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
        )
        return order

class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer für das Reviews-Modell, das Bewertungen von Benutzern für Business-Anbieter darstellt.
    
    Attributes:
        reviewer (PrimaryKeyRelatedField): Der Benutzer, der die Bewertung abgegeben hat.
    
    Meta:
        model: Reviews
        fields: Alle relevanten Felder der Bewertung.
    """
    reviewer = serializers.PrimaryKeyRelatedField(source='customer_user', read_only=True)
    class Meta:
        model = Review
        fields = ['id', 'business_user', 'reviewer', 'rating', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'customer_user']

    def create(self, validated_data):
        """
        Erstellt eine neue Bewertung für einen Business-Benutzer.
        """
        customer_user = validated_data.pop('customer_user')
        review = Review.objects.create(customer_user=customer_user, **validated_data)
        return review
    
    