from rest_framework import permissions,status,viewsets
from rest_framework.generics import RetrieveUpdateAPIView
from .serializer import UserProfileSerializer,UserProfileDetailSerializer,OfferSerializer,OfferDetailsSerializer
from ..models import UserProfile, Offers,OfferDetails
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

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
    serializer_class = UserProfileDetailSerializer
    def get_queryset(self):
        return UserProfile.objects.filter(type='business')
    
class CustomerProfilesViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileDetailSerializer
    def get_queryset(self):
        return UserProfile.objects.filter(type='customer')
    
class OffersViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Offers.objects.all()
    serializer_class = OfferSerializer
    
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
    
    def get_queryset(self):
        """
        Beschränkt das QuerySet auf die OfferDetails des authentifizierten Benutzers
        oder zeigt alle Einträge für Admins.
        """
        user = self.request.user
        if user.is_staff:  # Admins sehen alles
            return OfferDetails.objects.all()
        return OfferDetails.objects.filter(offer__user=user)  # Nur eigene OfferDetails