
from django.urls import path,include
from .views import UserProfileDetailView,BusinessProfilesViewSet, CustomerProfilesViewSet,OffersViewSet,OfferDetailsView,OrderViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'profiles/business', BusinessProfilesViewSet, basename='business-profiles')
router.register(r'profiles/customer', CustomerProfilesViewSet, basename='customer-profiles')
router.register(r'offerdetails', OfferDetailsView, basename='offer-detail')
router.register(r'offers', OffersViewSet, basename='offers')
router.register(r'orders', OrderViewSet, basename='oders')


urlpatterns = [
    path('', include(router.urls)),
    path('profile/<int:pk>/', UserProfileDetailView.as_view(), name='user_profile_detail'),
]
