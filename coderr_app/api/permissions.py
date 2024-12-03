from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS

from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrAdmin(BasePermission):
    """
    Erlaubt:
    - SAFE_METHODS für alle authentifizierten Benutzer.
    - DELETE, PUT, PATCH nur für den Owner (user) oder Admins.
    """
    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS sind immer erlaubt
        if request.method in SAFE_METHODS:
            return True

        # Überprüfen, ob der Benutzer der Owner ist oder ein Admin
        return bool(
            request.user and
            (request.user == obj.user or request.user.is_staff)
        )

class IsBusinessUser(BasePermission):
    """
    Erlaubt POST-Anfragen nur für Benutzer mit dem Typ 'business'.
    Andere Methoden werden von dieser Klasse nicht behandelt.
    """

    def has_permission(self, request, view):
        if request.method == 'POST':
            if request.user.is_authenticated and hasattr(request.user, 'user_profile'):
                return request.user.user_profile.type == 'business'
            return False
        return True

class IsCustomer(BasePermission):
    """
    Erlaubt POST-Anfragen nur für Benutzer mit dem Typ 'customer'.
    """

    def has_permission(self, request, view):
        if request.method == 'POST':
            # Prüfen, ob der Benutzer authentifiziert ist und ein UserProfile hat
            if request.user.is_authenticated and hasattr(request.user, 'user_profile'):
                return request.user.user_profile.type == 'customer'
            return False
        return True
    

class IsReviewerOrAdmin(BasePermission):
    """
    Erlaubt Aktionen nur für den Ersteller der Bewertung (reviewer) oder Admins.
    GET-Anfragen sind für alle erlaubt.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return request.user and (request.user == obj.customer_user or request.user.is_staff)        