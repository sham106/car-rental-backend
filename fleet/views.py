from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets, permissions, pagination, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Vehicle
from .serializers import VehicleSerializer

class StandardPagination(pagination.PageNumberPagination):
    page_size = 10
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 100

class VehicleViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing fleet assets.
    Provides: 
    - GET /api/vehicles/ (List with pagination)
    - POST /api/vehicles/ (Create)
    - GET /api/vehicles/{id}/ (Retrieve)
    - PUT/PATCH /api/vehicles/{id}/ (Update)
    - DELETE /api/vehicles/{id}/ (Delete)
    - GET /api/vehicles/count/ (Get total count)
    
    Query Parameters:
    - limit: Number of results to return (e.g., ?limit=3)
    - page: Page number for pagination
    - page_size: Results per page
    """
    queryset = Vehicle.objects.all().order_by('-created_at')
    serializer_class = VehicleSerializer
    pagination_class = StandardPagination
    
    def get_permissions(self):
        """
        Custom permissions:
        - List/Retrieve: Allow Any (Potential customers need to see the fleet)
        - Create/Update/Delete: Require Admin/Staff status
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
    
    def get_queryset(self):
        """Optionally filter vehicles by limit parameter for featured collections"""
        queryset = super().get_queryset()
        limit = self.request.query_params.get('limit')
        if limit:
            try:
                limit_int = int(limit)
                if limit_int > 0:
                    return queryset[:limit_int]
            except ValueError:
                pass
        return queryset
    
    @action(detail=False, methods=['get'], url_path='count')
    def count_vehicles(self, request):
        """Return total vehicle count for fleet size display"""
        count = Vehicle.objects.count()
        return Response({'count': count})
