from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('business', 'Business'),
        ('staff', 'Staff'),
    ]
    user= models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    location = models.CharField(max_length=50)
    email = models.EmailField( max_length=254)
    file = models.FileField( upload_to=None, max_length=100)
    description = models.TextField(max_length=300)
    tel = models.CharField(max_length=20)
    working_hours = models.CharField(max_length=25)
    created_at = models.DateTimeField( auto_now_add=False)
    type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')
    
    def __str__(self):
        return self.user.username
    
    class Meta:
        ordering = ['user__username']
        verbose_name_plural = 'User Profiles'


class Offers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offers')
    title = models.CharField( max_length=50)
    image = models.FileField( upload_to=None, max_length=100, blank=True, null=True)
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
    offer = models.OneToOneField(Offers, on_delete=models.CASCADE, related_name='details')
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

class order(models.Model):
    status_choices = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]
    customer_user=models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_order')
    business_user=models.ForeignKey(User, on_delete=models.CASCADE, related_name='business_order')
    status = models.CharField(max_length=20, choices=status_choices, default='pending')
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