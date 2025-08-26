from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api'

# Create a router for API views
router = DefaultRouter()

urlpatterns = [
    # API root
    path('', views.api_root, name='api-root'),
    
    # Authentication endpoints
    path('auth/', include([
        path('register/', views.UserRegistrationView.as_view(), name='user-register'),
        path('token/', views.CustomTokenObtainPairView.as_view(), name='token-obtain'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    ])),
    
    # User endpoints
    path('users/me/', views.UserProfileView.as_view(), name='user-profile'),
    
    # Event endpoints
    path('events/', include([
        path('', views.EventListCreateView.as_view(), name='event-list'),
        path('my-events/', views.UserEventsView.as_view(), name='user-events'),
        path('<int:pk>/', views.EventDetailView.as_view(), name='event-detail'),
        path('<int:event_id>/register/', views.EventRegistrationView.as_view(), name='event-register'),
    ])),
]
