from django.urls import path
from .views import RegisterView, UserProfileView, LoginView, UserListView, UserDetailView

urlpatterns = [
    path("login/", LoginView.as_view()),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('me/', UserProfileView.as_view(), name='user_me'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
]
