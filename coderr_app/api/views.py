from rest_framework import permissions,status,viewsets
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter,SearchFilter
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import RetrieveUpdateAPIView
from .serializer import OfferDetailSerializer, OfferListSerializer, UserProfileSerializer,ReviewSerializer,OffersSerializer,OfferDetailsSerializer, OrderSerializer,CustomerProfileSerializer,BusinesProfileSerializer
from ..models import UserProfile, Offers,OfferDetails,Order,Review
from django.db.models import Min, Max, Avg
from .permissions import IsOwnerOrAdmin,IsCustomer,IsBusinessUser,IsReviewerOrAdmin
from .pagination import OffersPagination
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django.db.models import Subquery, OuterRef, Min, Max


class UserProfileDetailView(RetrieveUpdateAPIView):
    """
    API-Endpunkt für Benutzerprofile.

    **Methoden**:
    - GET: Gibt die Profildetails des eines Benutzers zurück.
    - PATCH: Aktualisiert das Profil des authentifizierten Benutzers sowie zugehörige Benutzerdaten (z. B. Name, E-Mail).

    **Details**:
    - Nur authentifizierte Benutzer können diese View verwenden.
    - Benutzer können nur ihr eigenes Profil abrufen und bearbeiten.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated] 
    queryset = UserProfile.objects.all()
    
    def patch(self, request, *args, **kwargs):
        profile = self.get_object()
        user = profile.user
        
        if request.user != user and not request.user.is_staff:
            raise PermissionDenied("You do not have permission to edit this profile.")
        
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
    """
    API-Endpunkt für Geschäftsnutzer-Profile.

    **Methoden**:
    - GET: Gibt eine Liste aller Geschäftsnutzer zurück.
    - POST: Erstellt ein neues Geschäftsnutzer-Profil.
    - PUT: Aktualisiert ein Geschäftsnutzer-Profil vollständig.
    - PATCH: Aktualisiert ein Geschäftsnutzer-Profil teilweise.
    - DELETE: Löscht ein Geschäftsnutzer-Profil.

    **Details**:
    - Nur authentifizierte Benutzer können diese View verwenden.
    - Zeigt ausschließlich Profile mit `type='business'`.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = BusinesProfileSerializer
    
    def get_queryset(self):
        return UserProfile.objects.filter(type='business')
    
class CustomerProfilesViewSet(viewsets.ModelViewSet):
    """
    API-Endpunkt für Kundennutzer-Profile.

    **Methoden**:
    - GET: Gibt eine Liste aller Kundennutzer zurück.
    - POST: Erstellt ein neues Kundennutzer-Profil.
    - PUT: Aktualisiert ein Kundennutzer-Profil vollständig.
    - PATCH: Aktualisiert ein Kundennutzer-Profil teilweise.
    - DELETE: Löscht ein Kundennutzer-Profil.

    **Details**:
    - Nur authentifizierte Benutzer können diese View verwenden.
    - Zeigt ausschließlich Profile mit `type='customer'`.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
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
    """
    API-Endpunkt für Angebote (Offers).

    **Methoden**:
    - GET: Listet alle Angebote auf, gefiltert nach Authentifizierung und Berechtigungen.
    - POST: Erstellt ein neues Angebot.
    - PUT: Aktualisiert ein Angebot vollständig.
    - PATCH: Aktualisiert ein Angebot teilweise.
    - DELETE: Löscht ein Angebot und die zugehörigen Details.

    **Details**:
    - Nur authentifizierte Benutzer mit Berechtigungen (z. B. `IsBusinessUser`, `IsOwnerOrAdmin`) können diese View verwenden.
    - Unterstützt Filter, Suche und Sortierung.
    """
    permission_classes = [permissions.IsAuthenticated,IsBusinessUser,IsOwnerOrAdmin]
    serializer_class = OffersSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter,SearchFilter]
    filterset_class = OffersFilter 
    ordering_fields = ['updated_at', 'min_price']
    ordering = ['updated_at'] 
    search_fields = ['title', 'description']
    pagination_class = OffersPagination
    queryset=Offers.objects.all()
   
    def get_queryset(self):
        """
        Annotiert Angebote mit zusätzlichen Feldern.
        """
        return Offers.objects.annotate(
            min_price=Subquery(
                OfferDetails.objects.filter(offer=OuterRef('pk')).values('offer').annotate(
                    min_price=Min('price')
                ).values('min_price')
            ),
            min_delivery_time=Subquery(
                OfferDetails.objects.filter(offer=OuterRef('pk')).values('offer').annotate(
                    min_delivery_time=Min('delivery_time_in_days')
                ).values('min_delivery_time')
            ),
            max_delivery_time=Subquery(
                OfferDetails.objects.filter(offer=OuterRef('pk')).values('offer').annotate(
                    max_delivery_time=Max('delivery_time_in_days')
                ).values('max_delivery_time')
            )
        )
    def get_serializer_class(self):
        """
        Wählt den passenden Serializer basierend auf der Aktion aus.
        """
        if self.action == 'list':  # Für GET /offers/
            return OfferListSerializer
        if self.action == 'retrieve':  # Für GET /offers/<id>/
            return OfferDetailSerializer
        return OffersSerializer

    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
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
    """
    API-Endpunkt für Bestellungen (Orders).

    **Methoden**:
    - GET: Zeigt Bestellungen für den authentifizierten Benutzer (Admins sehen alle).
    - POST: Erstellt eine neue Bestellung.
    - PUT: Aktualisiert eine Bestellung vollständig (nur Owner oder Admins).
    - PATCH: Aktualisiert eine Bestellung teilweise (nur Owner oder Admins).
    - DELETE: Löscht eine Bestellung (nur Admins).

    **Details**:
    - Nur authentifizierte Benutzer mit entsprechenden Berechtigungen können diese View verwenden.
    """
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated,IsCustomer]

      
    def get_queryset(self):
        user = self.request.user
        
        if user.is_staff:
            return Order.objects.all()
        
        return Order.objects.filter(customer_user=user) | Order.objects.filter(business_user=user)
    
    def update(self, request, *args, **kwargs):
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
    Gibt die Anzahl der Bestellungen mit dem Status `in_progress` für einen Geschäftsnutzer zurück.

    **Methoden**:
    - GET: Liefert die Anzahl der laufenden Bestellungen (`order_count`).

    **Parameter**:
    - `business_user_id`: ID des Geschäftsnutzers.

    **Antwort**:
    - 200 OK: Gibt die Anzahl der laufenden Bestellungen zurück.
    - 403 Forbidden: Wenn der Benutzer kein Geschäftsnutzer ist.
    - 404 Not Found: Wenn der Geschäftsnutzer nicht existiert.
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
    Gibt die Anzahl der abgeschlossenen Bestellungen (`completed`) für einen Geschäftsnutzer zurück.

    **Methoden**:
    - GET: Liefert die Anzahl der abgeschlossenen Bestellungen (`completed_order_count`).

    **Parameter**:
    - `business_user_id`: ID des Geschäftsnutzers.

    **Antwort**:
    - 200 OK: Gibt die Anzahl der abgeschlossenen Bestellungen zurück.
    - 403 Forbidden: Wenn der Benutzer kein Geschäftsnutzer ist.
    - 404 Not Found: Wenn der Geschäftsnutzer nicht existiert.
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
    
class ReviewsFilter(filters.FilterSet):
    """
    FilterSet zum Filtern von Bewertungen.

    **Felder**:
    - **business_user_id**: ID des Geschäftsbenutzers, dessen Bewertungen abgerufen werden sollen.
    - **reviewer_id**: ID des Kunden, der die Bewertung abgegeben hat.

    **Verwendete Modelle**: Reviews
    """
    business_user_id = filters.NumberFilter(field_name='business_user__id')
    reviewer_id = filters.NumberFilter(field_name='customer_user__id')

    class Meta:
        model = Review
        fields = ['business_user_id', 'reviewer_id']
        
class ReviewViewSet(viewsets.ModelViewSet):
    """
    API-Endpunkt für Reviews (Listenansicht und Erstellung).
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewerOrAdmin] 

    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ReviewsFilter
    ordering_fields = ['rating', 'updated_at']
    
    def perform_create(self, serializer):
        serializer.save(customer_user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class BaseInfoView(APIView):
    """
    API-Endpunkt für allgemeine Basisinformationen.

    **Methoden**:
    - GET: Gibt Statistiken zur Plattform zurück (Anzahl der Bewertungen, Angebote, etc.).

    **Details**:
    - Keine Authentifizierung erforderlich.
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