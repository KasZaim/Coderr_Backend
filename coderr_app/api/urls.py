
from django.urls import path,include
from .views import UserProfileDetailView,BusinessProfilesViewSet, CustomerProfilesViewSet,OffersViewSet,OfferDetailsView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'profiles/business', BusinessProfilesViewSet, basename='business-profiles')
router.register(r'profiles/customer', CustomerProfilesViewSet, basename='customer-profiles')
router.register(r'offers', OffersViewSet, basename='offers')
router.register(r'offerdetails', OfferDetailsView, basename='offer-detail')


urlpatterns = [
    path('', include(router.urls)),
    path('profile/<int:pk>/', UserProfileDetailView.as_view(), name='user_profile_detail'),
]
