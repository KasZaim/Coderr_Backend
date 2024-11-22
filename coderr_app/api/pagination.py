from rest_framework.pagination import PageNumberPagination

class OffersPagination(PageNumberPagination):
    page_size_query_param = 'page_size'  # Ermöglicht Anpassung der Seitengröße per Query-Parameter
    page_size = 6 