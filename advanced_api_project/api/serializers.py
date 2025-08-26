from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .models import Event
from django.utils import timezone

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token obtain serializer to include user data in the response."""
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['user'] = UserSerializer(self.user).data
        return data


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""
    password = serializers.CharField(write_only=True, required=False)
    events_organized = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    attending_events = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'password', 'is_active', 'date_joined', 'events_organized',
            'attending_events'
        ]
        read_only_fields = ['is_active', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def create(self, validated_data):
        """Create and return a new user with encrypted password."""
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        """Update and return an existing user instance."""
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)


class EventSerializer(serializers.ModelSerializer):
    """Serializer for the Event model."""
    organizer = UserSerializer(read_only=True)
    attendees = UserSerializer(many=True, read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    can_register = serializers.SerializerMethodField()
    attendee_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'date_time', 'location',
            'capacity', 'organizer', 'attendees', 'created_at',
            'updated_at', 'is_full', 'can_register', 'attendee_count'
        ]
        read_only_fields = ['organizer', 'created_at', 'updated_at', 'is_full']

    def get_attendee_count(self, obj):
        """Get the number of attendees for the event."""
        return obj.attendees.count()

    def get_can_register(self, obj):
        """Check if the current user can register for this event."""
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return obj.can_register(request.user)
        return False

    def validate_date_time(self, value):
        """Validate that the event date is in the future."""
        if value < timezone.now():
            raise serializers.ValidationError("Event date cannot be in the past.")
        return value

    def create(self, validated_data):
        """Create a new event with the current user as the organizer."""
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['organizer'] = request.user
            return super().create(validated_data)
        raise serializers.ValidationError("You must be logged in to create an event.")


class EventRegistrationSerializer(serializers.Serializer):
    """Serializer for event registration."""
    user_id = serializers.IntegerField()

    def validate_user_id(self, value):
        """Validate that the user exists."""
        try:
            User.objects.get(pk=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")
        return value
