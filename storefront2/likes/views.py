from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import LikedItem
from .serializers import LikedItemSerializer


class LikeViewSet(ModelViewSet):
    queryset = LikedItem.objects.all()
    serializer_class = LikedItemSerializer