from rest_framework import permissions,status,viewsets
from rest_framework.generics import RetrieveUpdateAPIView
from .serializer import UserProfileSerializer,UserProfileDetailSerializer,OfferSerializer,OfferDetailsSerializer, OrderSerializer,CustomerProfileSerializer
from ..models import UserProfile, Offers,OfferDetails,Order
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Min, Max
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from rest_framework.filters import OrderingFilter,SearchFilter
from .permissions import IsOwnerOrAdmin,IsCustomer,IsBusinessUser
from .pagination import OffersPagination

class UserProfileDetailView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated] 
    
    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)

    def patch(self, request, *args, **kwargs):
        profile = self.get_object()
        user = profile.user
        
        for field in ['first_name', 'last_name', 'email']:
            if field in request.data:
                setattr(user, field, request.data[field])
        user.save()
        
        serializer = self.serializer_class(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BusinessProfilesViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomerProfileSerializer
    
    def get_queryset(self):
        return UserProfile.objects.filter(type='business')
    
class CustomerProfilesViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomerProfileSerializer
    def get_queryset(self):
        return UserProfile.objects.filter(type='customer')
    
class OffersFilter(filters.FilterSet):
    creator_id = filters.NumberFilter(field_name="user_id", lookup_expr='exact')  
    min_price = filters.NumberFilter(field_name="min_price", lookup_expr='gte') 
    max_delivery_time = filters.NumberFilter(field_name="max_delivery_time", lookup_expr='lte') 

    class Meta:
        model = Offers
        fields = ['creator_id', 'min_price', 'max_delivery_time']

class OffersViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated,IsBusinessUser,IsOwnerOrAdmin]
    serializer_class = OfferSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter,SearchFilter]
    filterset_class = OffersFilter 
    ordering_fields = ['updated_at', 'min_price']
    ordering = ['updated_at'] 
    search_fields = ['title', 'description']
    pagination_class = OffersPagination

    def get_queryset(self):
        """
        Beschränkt das QuerySet auf die Angebote des authentifizierten Benutzers
        und fügt aggregierte Felder hinzu.
        """
        user = self.request.user

        queryset = Offers.objects.all().annotate(
            min_price=Min('details__price'),
            min_delivery_time=Min('details__delivery_time_in_days'),
            max_delivery_time=Max('details__delivery_time_in_days')
        )
        return queryset
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        OfferDetails.objects.filter(offer=instance).delete()
        instance.delete()
        return Response(
            {"message": "Offer and its details were deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
    
    
        
class OfferDetailsView(viewsets.ModelViewSet):
    """
    View für das Abrufen eines spezifischen OfferDetails.
    """
    permission_classes = [permissions.IsAuthenticated] #isOwnerOrAdmin
    queryset = OfferDetails.objects.all()
    serializer_class = OfferDetailsSerializer
    
    def get_serializer_context(self):
        """
        Fügt die Anfrage zum Serializer-Kontext hinzu.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    
    
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated,IsCustomer]

      
    def get_queryset(self):
        """
        Zeigt Bestellungen nur für den authentifizierten Benutzer.
        Admins sehen alle Bestellungen.
        """
        user = self.request.user
        
        if user.is_staff:
            return Order.objects.all()
        
        return Order.objects.filter(customer_user=user) | Order.objects.filter(business_user=user)
    
    def update(self, request, *args, **kwargs):
        """
        Erlaubt nur dem Owner (customer_user oder business_user), Änderungen vorzunehmen.
        """
        instance = self.get_object()
        
        if not request.user.is_staff and request.user != instance.business_user:
            return Response(
                {"detail": "You do not have permission to update this order."},
                status=status.HTTP_403_FORBIDDEN
            )
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
        
    def destroy(self, request, *args, **kwargs):
        """
        Erlaubt nur Admins, eine Bestellung zu löschen.
        """
        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff members can delete orders."},
                status=status.HTTP_403_FORBIDDEN
            )

        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Order successfully deleted."},
            status=status.HTTP_204_NO_CONTENT
        )
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    