from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from apis.serializers import UserSerializer, GroupSerializer
from django.http import HttpResponse, JsonResponse
import requests

def index(request):
    r = requests.get('https://api.rezdy.com/v1/products/marketplace?apiKey=1d7ce4142c634882846e3597aaef36e4')    
    return render(request, "apis/index.html", r.json())

def download(request):
    data = requests.get('https://api.rezdy.com/v1/products/marketplace?apiKey=1d7ce4142c634882846e3597aaef36e4')
    return JsonResponse(data.json())

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
