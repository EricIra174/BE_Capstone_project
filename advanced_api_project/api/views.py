from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Event, User
from .serializers import (
    UserSerializer, EventSerializer, EventRegistrationSerializer,
    CustomTokenObtainPairSerializer
)


class UserRegistrationView(generics.CreateAPIView):
    """View for user registration."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """View for viewing and updating user profile."""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token obtain view that includes user data in the response."""
    serializer_class = CustomTokenObtainPairSerializer


class EventListCreateView(generics.ListCreateAPIView):
    """View for listing and creating events."""
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['date_time', 'created_at', 'title']
    filterset_fields = {
        'date_time': ['gte', 'lte', 'exact', 'gt', 'lt'],
        'capacity': ['gte', 'lte', 'exact', 'gt', 'lt'],
    }

    def get_queryset(self):
        """Return events filtered by query parameters."""
        queryset = Event.objects.all()
        
        # Filter for upcoming events only if requested
        upcoming = self.request.query_params.get('upcoming', None)
        if upcoming and upcoming.lower() == 'true':
            queryset = queryset.filter(date_time__gte=timezone.now())
            
        # Order by date_time by default for upcoming events
        if not self.request.query_params.get('ordering'):
            queryset = queryset.order_by('date_time')
            
        return queryset

    def perform_create(self, serializer):
        """Set the organizer to the current user when creating an event."""
        serializer.save(organizer=self.request.user)


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for retrieving, updating and deleting events."""
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Optimize queryset by selecting related fields."""
        return Event.objects.select_related('organizer').prefetch_related('attendees')
    
    def perform_update(self, serializer):
        """Only allow the organizer to update the event."""
        if serializer.instance.organizer != self.request.user:
            raise permissions.PermissionDenied("You do not have permission to edit this event.")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Only allow the organizer to delete the event."""
        if instance.organizer != self.request.user:
            raise permissions.PermissionDenied("You do not have permission to delete this event.")
        instance.delete()


class EventRegistrationView(APIView):
    """View for registering and unregistering from events."""
    permission_classes = [IsAuthenticated]

    def post(self, request, event_id):
        """Register the current user for an event."""
        event = get_object_or_404(Event, pk=event_id)
        
        # Check if the event is already full
        if event.is_full():
            return Response(
                {"detail": "This event is already full."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Check if user is already registered
        if event.attendees.filter(pk=request.user.pk).exists():
            return Response(
                {"detail": "You are already registered for this event."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Register the user
        event.attendees.add(request.user)
        return Response(
            {"detail": "Successfully registered for the event."},
            status=status.HTTP_200_OK
        )
    
    def delete(self, request, event_id):
        """Unregister the current user from an event."""
        event = get_object_or_404(Event, pk=event_id)
        
        if not event.attendees.filter(pk=request.user.pk).exists():
            return Response(
                {"detail": "You are not registered for this event."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        event.attendees.remove(request.user)
        return Response(
            {"detail": "Successfully unregistered from the event."},
            status=status.HTTP_200_OK
        )


class UserEventsView(generics.ListAPIView):
    """View for listing events that the current user is attending or organizing."""
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return events that the user is attending or organizing."""
        user = self.request.user
        event_type = self.request.query_params.get('type', 'attending')
        
        if event_type == 'organized':
            return Event.objects.filter(organizer=user).order_by('date_time')
        else:  # Default to 'attending'
            return user.attending_events.all().order_by('date_time')


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    """API root view that provides links to all the API endpoints."""
    return Response({
        'users': {
            'register': request.build_absolute_uri('auth/register/'),
            'token-obtain': request.build_absolute_uri('auth/token/'),
            'token-refresh': request.build_absolute_uri('auth/token/refresh/'),
            'profile': request.build_absolute_uri('users/me/'),
        },
        'events': {
            'list': request.build_absolute_uri('events/'),
            'my-events': {
                'attending': request.build_absolute_uri('events/my-events/?type=attending'),
                'organized': request.build_absolute_uri('events/my-events/?type=organized'),
            },
            'register': 'To register for an event, send a POST request to /api/events/{id}/register/',
        },
    })
