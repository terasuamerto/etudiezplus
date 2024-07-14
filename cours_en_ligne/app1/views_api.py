from rest_framework import viewsets
from .models import UserProfile, Subscription, Cours, Lecon
from .serializers import UserProfileSerializer, SubscriptionSerializer, CoursSerializer, LeconSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

class CoursViewSet(viewsets.ModelViewSet):
    queryset = Cours.objects.all()
    serializer_class = CoursSerializer

class LeconViewSet(viewsets.ModelViewSet):
    queryset = Lecon.objects.all()
    serializer_class = LeconSerializer
