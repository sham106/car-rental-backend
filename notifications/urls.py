from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='list'),
    path('unread-count/', views.NotificationUnreadCountView.as_view(), name='unread-count'),
    path('mark-read/', views.NotificationMarkReadView.as_view(), name='mark-read'),
    path('mark-all-read/', views.mark_all_read, name='mark-all-read'),
    path('<int:notification_id>/read/', views.mark_notification_read, name='mark-read-single'),
]
