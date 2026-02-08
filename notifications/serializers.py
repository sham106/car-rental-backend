from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notification model"""
    time_ago = serializers.ReadOnlyField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type', 
            'priority', 'link', 'is_read', 'created_at', 'time_ago'
        ]
        read_only_fields = ['id', 'created_at', 'time_ago']


class NotificationMarkReadSerializer(serializers.Serializer):
    """Serializer for marking notifications as read"""
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text='List of notification IDs to mark as read. If empty, marks all as read.'
    )
    mark_all = serializers.BooleanField(
        default=False,
        help_text='If true, marks all notifications as read'
    )
