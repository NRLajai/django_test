from rest_framework import serializers
from .models import LikedItem


class LikedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikedItem
        fields = '__all__'