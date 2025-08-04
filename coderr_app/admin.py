from django.contrib import admin
from .models import UserProfile, Offers, OfferDetails, Order, Review


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'created_at')  
    search_fields = ('user__username', 'type')     
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'offer', 'business_user')  
    
    
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Offers)
admin.site.register(OfferDetails)
admin.site.register(Order,OrderAdmin)
admin.site.register(Review)