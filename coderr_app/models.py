from django.db import models
from django.contrib.auth.models import User
from django.db.models import Min, Max

class UserProfile(models.Model):
    """
    Modell für Benutzerprofile.

    **Felder**:
    - `user`: Verknüpfung mit dem Django-Benutzer.
    - `location`: Standort des Benutzers.
    - `email`: E-Mail-Adresse des Benutzers.
    - `file`: Profilbild des Benutzers.
    - `description`: Beschreibung des Benutzers.
    - `tel`: Telefonnummer des Benutzers.
    - `working_hours`: Arbeitszeiten des Benutzers.
    - `created_at`: Datum und Uhrzeit der Erstellung des Profils.
    - `type`: Benutzerrolle (z. B. Kunde, Geschäftsnutzer, Mitarbeiter).

    **Zusätzliche Informationen**:
    - Der Benutzer kann entweder Kunde, Geschäftsnutzer oder Mitarbeiter sein.
    - Profile werden standardmäßig nach Benutzernamen sortiert.
    """
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('business', 'Business'),
        ('staff', 'Staff'),
    ]
    user= models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    location = models.CharField(max_length=50)
    email = models.EmailField( max_length=254)
    file = models.FileField( upload_to='profile_img/', max_length=100)
    description = models.TextField(max_length=300)
    tel = models.CharField(max_length=20)
    working_hours = models.CharField(max_length=25)
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')
    
    def __str__(self):
        return self.user.username
    
    class Meta:
        ordering = ['user__username']
        verbose_name_plural = 'User Profiles'


class Offers(models.Model):
    """
    Modell für Angebote.

    **Felder**:
    - `user`: Benutzer, der das Angebot erstellt hat.
    - `title`: Titel des Angebots.
    - `image`: Optionales Bild zum Angebot.
    - `description`: Beschreibung des Angebots.
    - `created_at`: Datum und Uhrzeit der Erstellung des Angebots.
    - `updated_at`: Datum und Uhrzeit der letzten Aktualisierung des Angebots.

    **Zusätzliche Informationen**:
    - Angebote werden standardmäßig alphabetisch nach Titel sortiert.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offers')
    title = models.CharField(max_length=50)
    image = models.FileField(upload_to=None, max_length=100, blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField( auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['title']
        verbose_name_plural = 'Offers'

        
class OfferDetails(models.Model):
    OFFER_TYPES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium')
    ]
    offer = models.ForeignKey(Offers, on_delete=models.CASCADE, related_name='details')
    title = models.CharField(max_length=200, default="Offer Details")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_time_in_days = models.PositiveIntegerField(default=1 ,help_text='only positive integers allowed')
    revisions = models.IntegerField(default=-1, help_text="-1 means unlimited revisions")
    additional_information = models.TextField(blank=True, help_text="Additional information for the offer")
    features = models.JSONField()
    offer_type = models.CharField(max_length=50, choices=OFFER_TYPES)
    
    def __str__(self):
        return f"Details for {self.offer.title}"
    
    class Meta:
        ordering = ['offer']
        verbose_name_plural = 'Offer Details'

class Order(models.Model):
    status_choices = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]
    customer_user=models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_order')
    business_user=models.ForeignKey(User, on_delete=models.CASCADE, related_name='business_order')
    offer=models.ForeignKey(Offers, on_delete=models.CASCADE, related_name='order' )
    offer_detail=models.ForeignKey(OfferDetails, on_delete=models.CASCADE, related_name='order_details')
    status = models.CharField(max_length=20, choices=status_choices, default='in_progress')
    title = models.CharField(max_length=50)
    revisions = models.IntegerField(default=-1, help_text="-1 means unlimited revisions")
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField()
    offer_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Order by {self.customer_user.username} for {self.title}'
    
    class Meta:
        ordering = ['title']
        verbose_name_plural = 'Orders'
        
class Review(models.Model):
    business_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="business_reviews", limit_choices_to={'user_profile__type': 'business'})
    customer_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer_reviews",limit_choices_to={'user_profile__type': 'customer'})
    rating = models.PositiveSmallIntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']  

    def __str__(self):
        return f"Review by {self.customer_user} for {self.business_user} (Rating: {self.rating})"