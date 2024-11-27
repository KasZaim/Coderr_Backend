from django.urls import reverse
from rest_framework import serializers
from ..models import UserProfile, Offers, OfferDetails,Order,Review
from django.conf import settings
from django.contrib.auth.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer für das UserProfile-Modell.

    Fügt zusätzliche Felder aus dem User-Modell hinzu, wie `username`, `first_name` und `last_name`. Beinhaltet auch Profilinformationen wie Standort, E-Mail und Beschreibung.

    Attributes:
    user (PrimaryKeyRelatedField): Benutzer, dem das Profil gehört (read-only).
    username (CharField): Benutzername des zugehörigen Benutzers (read-only).
    first_name (CharField): Vorname des Benutzers (read-only).
    last_name (CharField): Nachname des Benutzers (read-only).
    location (CharField): Standort des Benutzers.
    email (EmailField): E-Mail-Adresse des Benutzers.
    file (FileField): Profilbild oder Datei des Benutzers.
    description (TextField): Beschreibung oder Biografie des Benutzers.
    tel (CharField): Telefonnummer des Benutzers.
    working_hours (CharField): Arbeitszeiten des Benutzers.
    type (CharField): Typ des Benutzers (z. B. 'customer', 'business').
    created_at (DateTimeField): Zeitpunkt der Profilerstellung (read-only).

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

    Attributes:
    user (SerializerMethodField): Verschachtelte Benutzerinformationen, einschließlich `pk`, `username`, `first_name` und `last_name`.
    file (FileField): Profilbild oder Datei des Benutzers.
    location (CharField): Standort des Benutzers.
    tel (CharField): Telefonnummer des Benutzers.
    description (TextField): Beschreibung oder Biografie des Benutzers.
    working_hours (CharField): Arbeitszeiten des Benutzers.
    type (CharField): Typ des Benutzers (z. B. 'customer', 'business') (read-only).

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

    Attributes:
    user (SerializerMethodField): Verschachtelte Benutzerinformationen.
    file (FileField): Profilbild oder Datei des Kunden.
    created_at (DateTimeField): Zeitpunkt der Profilerstellung.
    type (CharField): Typ des Benutzers, standardmäßig 'customer' (read-only).

    Meta:
    model: UserProfile
    fields: ['user', 'file', 'created_at', 'type']
    read_only_fields: ['type']
    """

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
    """
    Serializer für das OfferDetails-Modell.

    Verarbeitet die Details eines Angebots, einschließlich Preis, Lieferzeit und spezifische Merkmale.

    Attributes:
    id (IntegerField): Primärschlüssel des Angebotsdetails (read-only).
    title (CharField): Titel des Angebotsdetails.
    price (DecimalField): Preis des Angebotsdetails.
    offer (PrimaryKeyRelatedField): Zugehöriges Angebot (read-only).
    delivery_time_in_days (IntegerField): Lieferzeit in Tagen.
    revisions (IntegerField): Anzahl der erlaubten Überarbeitungen.
    additional_information (TextField): Zusätzliche Informationen zum Angebot.
    features (JSONField): Merkmale oder Funktionen des Angebots.
    offer_type (CharField): Typ des Angebotsdetails (z. B. 'basic', 'standard', 'premium').

    Meta:
    model: OfferDetails
    fields: Alle oben genannten Felder.
    read_only_fields: ['id', 'offer']
    """

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
    """
    Serializer für das Offers-Modell.

    Verarbeitet Angebote und deren Details, einschließlich Benutzerinformationen und Preis-/Lieferzeitberechnungen.

    Attributes:
    id (IntegerField): Primärschlüssel des Angebots (read-only).
    title (CharField): Titel des Angebots.
    min_delivery_time (IntegerField): Minimale Lieferzeit über alle Angebotsdetails hinweg (read-only).
    max_delivery_time (IntegerField): Maximale Lieferzeit über alle Angebotsdetails hinweg (read-only).
    min_price (DecimalField): Niedrigster Preis über alle Angebotsdetails hinweg (read-only).
    user (PrimaryKeyRelatedField): Benutzer, der das Angebot erstellt hat (read-only).
    user_details (SerializerMethodField): Zusätzliche Informationen über den Benutzer, wie `first_name`, `last_name` und `username`.
    image (FileField): Bild des Angebots.
    description (TextField): Beschreibung des Angebots.
    details (OfferDetailsSerializer): Liste der zugehörigen Angebotsdetails.
    created_at (DateTimeField): Zeitpunkt der Angebotserstellung (read-only).
    updated_at (DateTimeField): Zeitpunkt der letzten Aktualisierung (read-only).

    Meta:
    model: Offers
    fields: Alle oben genannten Felder.
    read_only_fields: ['id', 'created_at', 'updated_at']

    Methoden:
    get_user_details(self, obj): Gibt die Benutzerinformationen für das 'user_details'-Feld zurück.
    create(self, validated_data): Erstellt ein neues Angebot zusammen mit seinen Details.
    update(self, instance, validated_data): Aktualisiert ein bestehendes Angebot und seine Details.
    """

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
    """
    Serializer für das Order-Modell.

    Verarbeitet Bestellungen, die auf Angebotsdetails basieren, und stellt sicher, dass relevante Felder korrekt gesetzt werden.

    Attributes:
    id (IntegerField): Primärschlüssel der Bestellung (read-only).
    status (CharField): Status der Bestellung.
    business_user (PrimaryKeyRelatedField): Geschäftsnutzer, der die Bestellung bearbeitet (read-only).
    customer_user (PrimaryKeyRelatedField): Kunde, der die Bestellung aufgegeben hat (read-only).
    title (CharField): Titel der Bestellung, basierend auf dem Angebotsdetail (read-only).
    revisions (IntegerField): Anzahl der erlaubten Überarbeitungen (read-only).
    delivery_time_in_days (IntegerField): Lieferzeit in Tagen (read-only).
    price (DecimalField): Preis der Bestellung (read-only).
    features (JSONField): Merkmale oder Funktionen der Bestellung (read-only).
    offer_type (CharField): Typ des Angebots (read-only).
    created_at (DateTimeField): Zeitpunkt der Bestellung (read-only).
    updated_at (DateTimeField): Zeitpunkt der letzten Aktualisierung (read-only).
    offer_detail_id (IntegerField): ID des Angebotsdetails, auf dem die Bestellung basiert (write-only).

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
    Serializer für das Review-Modell.

    Verarbeitet Bewertungen, die von Kunden für Geschäftsnutzer erstellt werden, und stellt sicher, dass nur autorisierte Benutzer Bewertungen erstellen können.

    Attributes:
    id (IntegerField): Primärschlüssel der Bewertung (read-only).
    business_user (PrimaryKeyRelatedField): Geschäftsnutzer, der bewertet wird (read-only nach Erstellung).
    reviewer (PrimaryKeyRelatedField): Kunde, der die Bewertung abgibt (read-only).
    rating (IntegerField): Bewertung, typischerweise auf einer Skala von 1 bis 5.
    description (TextField): Textuelle Beschreibung oder Kommentare zur Bewertung.
    created_at (DateTimeField): Zeitpunkt der Erstellung der Bewertung (read-only).
    updated_at (DateTimeField): Zeitpunkt der letzten Aktualisierung (read-only).

    Meta:
    model: Review
    fields: ['id', 'business_user', 'reviewer', 'rating', 'description', 'created_at', 'updated_at']
    read_only_fields: ['reviewer', 'business_user', 'created_at', 'updated_at']

    Hinweis:
    - `business_user` ist beim Erstellen erforderlich, aber nach der Erstellung schreibgeschützt.
    - `reviewer` wird automatisch auf den aktuell authentifizierten Benutzer gesetzt.
    """

    business_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(user_profile__type='business'))
    reviewer = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'business_user', 'reviewer', 'rating', 'description', 'created_at', 'updated_at']
        read_only_fields = ['reviewer','business_user','created_at', 'updated_at']