from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Notification
from .serializers import NotificationSerializer, NotificationMarkReadSerializer

User = get_user_model()


class NotificationListView(generics.ListAPIView):
    """
    List all notifications for the authenticated user.
    Admins see all notifications, regular users see their own.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            # Admin sees all notifications
            return Notification.objects.all()
        else:
            # Regular user sees only their notifications
            return Notification.objects.filter(user=user)
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        unread_count = self.get_queryset().filter(is_read=False).count()
        return Response({
            'notifications': response.data,
            'unread_count': unread_count,
            'total_count': self.get_queryset().count()
        })


class NotificationUnreadCountView(generics.GenericAPIView):
    """
    Get unread notification count for the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        if user.is_staff:
            count = Notification.objects.filter(is_read=False).count()
        else:
            count = Notification.objects.filter(user=user, is_read=False).count()
        return Response({'unread_count': count})


class NotificationMarkReadView(generics.GenericAPIView):
    """
    Mark notifications as read.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationMarkReadSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        data = serializer.validated_data
        mark_all = data.get('mark_all', False)
        notification_ids = data.get('notification_ids', [])
        
        queryset = user.is_staff and Notification.objects.all() or Notification.objects.filter(user=user)
        
        if mark_all:
            # Mark all as read
            queryset.filter(is_read=False).update(is_read=True, created_at=Notification.created_at)  # Keep original timestamp
            return Response({'message': 'All notifications marked as read'})
        elif notification_ids:
            # Mark specific notifications as read
            updated = queryset.filter(id__in=notification_ids, is_read=False).update(is_read=True)
            return Response({'message': f'{updated} notifications marked as read'})
        else:
            return Response({'error': 'Please provide notification_ids or mark_all=true'}, 
                           status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def mark_notification_read(request, notification_id):
    """
    Mark a single notification as read.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    try:
        notification = Notification.objects.get(id=notification_id)
        
        # Check if user has access
        user = request.user
        if not user.is_staff and notification.user != user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        notification.is_read = True
        notification.save()
        
        return Response({'message': 'Notification marked as read'})
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def mark_all_read(request):
    """
    Mark all notifications as read for the current user.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    user = request.user
    if user.is_staff:
        Notification.objects.filter(is_read=False).update(is_read=True)
    else:
        Notification.objects.filter(user=user, is_read=False).update(is_read=True)
    
    return Response({'message': 'All notifications marked as read'})
