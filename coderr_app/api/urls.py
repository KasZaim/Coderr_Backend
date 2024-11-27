
from django.urls import path,include
from .views import UserProfileDetailView,BusinessProfilesViewSet,BaseInfoView, CustomerProfilesViewSet,OffersViewSet,CompletedOrderCountView,OfferDetailsView,OrderViewSet,OrderCountView,ReviewViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'profiles/business', BusinessProfilesViewSet, basename='business-profiles')
router.register(r'profiles/customer', CustomerProfilesViewSet, basename='customer-profiles')
router.register(r'offerdetails', OfferDetailsView, basename='offer-detail')
router.register(r'offers', OffersViewSet, basename='offers')
router.register(r'orders', OrderViewSet, basename='oders')
router.register(r'reviews', ReviewViewSet, basename='reviews')


urlpatterns = [
    path('', include(router.urls)),
    path('profile/<int:pk>/', UserProfileDetailView.as_view(), name='user_profile_detail'),
    path('order-count/<int:business_user_id>/', OrderCountView.as_view(), name='order-count'),
    path('completed-order-count/<int:business_user_id>/', CompletedOrderCountView.as_view(), name='completed,order-count'),
    path('base-info/', BaseInfoView.as_view(), name='base-info')
]
