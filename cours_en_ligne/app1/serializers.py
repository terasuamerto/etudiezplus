from rest_framework import serializers
from .models import UserProfile, Subscription, Cours, Lecon

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'

class CoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cours
        fields = '__all__'

class LeconSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecon
        fields = '__all__'
