from rest_framework import permissions,status,viewsets
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter,SearchFilter
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import RetrieveUpdateAPIView
from .serializer import UserProfileSerializer,ReviewSerializer,OfferSerializer,OfferDetailsSerializer, OrderSerializer,CustomerProfileSerializer
from ..models import UserProfile, Offers,OfferDetails,Order,Review
from django.db.models import Min, Max, Avg, Count
from .permissions import IsOwnerOrAdmin,IsCustomer,IsBusinessUser,IsReviewerOrAdmin
from .pagination import OffersPagination
from rest_framework.views import APIView

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

class OrderCountView(APIView):
    """
    Gibt die Anzahl der laufenden Bestellungen eines Geschäftsnutzers zurück.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, business_user_id):
        try:
            user_profile = UserProfile.objects.get(user__id=business_user_id)
            if user_profile.type != 'business':
                return Response({"detail": "User is not a business user."}, status=403)
        except UserProfile.DoesNotExist:
            return Response({"detail": "Business user not found."}, status=404)

        count = Order.objects.filter(business_user_id=business_user_id, status='in_progress').count()
        return Response({"order_count": count})

class CompletedOrderCountView(APIView):
    """
    Gibt die Anzahl der abgeschlossenen Bestellungen eines Geschäftsnutzers zurück.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, business_user_id):
        try:
            user_profile = UserProfile.objects.get(user__id=business_user_id)
            if user_profile.type != 'business':
                return Response({"detail": "User is not a business user."}, status=403)
        except UserProfile.DoesNotExist:
            return Response({"detail": "Business user not found."}, status=404)

        count = Order.objects.filter(business_user_id=business_user_id, status='completed').count()
        return Response({"completed_order_count": count})
    

class ReviewViewSet(viewsets.ModelViewSet):
    """
    API-Endpunkt für Reviews (Listenansicht und Erstellung).
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,IsReviewerOrAdmin]

    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_fields = ['business_user', 'reviewer']
    ordering_fields = ['rating', 'updated_at']
    
    def get_queryset(self):
        """
        Filtert die Reviews basierend auf `business_user_id` und `reviewer_id`.
        """
        
        queryset = super().get_queryset()
        business_user_id = self.request.query_params.get('business_user_id')
        reviewer_id = self.request.query_params.get('reviewer_id')
        
        if business_user_id:
            queryset = queryset.filter(business_user_id= business_user_id)
            
        if reviewer_id:
            queryset = queryset.filter(reviewer_id=reviewer_id)
            
        return queryset
    
    def create(self, request, *args, **kwargs):
        """
        Erstellt eine neue Bewertung. Nur Kunden können Bewertungen erstellen.
        """
        
        if request.user.user_profile.type != 'customer':
            return Response(
                {"detail": "Only customers can submit reviews."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        business_user_id = request.data.get('business_user')
        if Review.objects.filter(business_user_id=business_user_id, reviewer=request.user).exists():
            return Response(
                {"detail": "You have already submitted a review for this business user."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(reviewer=request.user)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
class BaseInfoView(APIView):
    """
    API-Endpunkt, der allgemeine Basisinformationen zur Plattform bereitstellt.
    """

    def get(self, request, format=None):
        review_count = Review.objects.count()
        
        average_rating = Review.objects.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0.0
        average_rating = round(average_rating, 1)
        
        business_profile_count = UserProfile.objects.filter(type='business').count()
        offer_count = Offers.objects.count()

        data = {
            "review_count": review_count,
            "average_rating": average_rating,
            "business_profile_count": business_profile_count,
            "offer_count": offer_count,
        }

        return Response(data, status=status.HTTP_200_OK)