from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets, permissions
from .models import Vehicle
from .serializers import VehicleSerializer

class VehicleViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing fleet assets.
    Provides: 
    - GET /api/vehicles/ (List)
    - POST /api/vehicles/ (Create)
    - GET /api/vehicles/{id}/ (Retrieve)
    - PUT/PATCH /api/vehicles/{id}/ (Update)
    - DELETE /api/vehicles/{id}/ (Delete)
    """
    queryset = Vehicle.objects.all().order_by('-created_at')
    serializer_class = VehicleSerializer
    
    def get_permissions(self):
        """
        Custom permissions:
        - List/Retrieve: Allow Any (Potential customers need to see the fleet)
        - Create/Update/Delete: Require Admin/Staff status
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
