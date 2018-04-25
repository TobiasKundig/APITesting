from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from apis.serializers import UserSerializer, GroupSerializer
from django.http import HttpResponse, JsonResponse
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from rest_auth.registration.views import SocialLoginView
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response


def index(request):
    return render(request, "apis/index.html")


@api_view(['GET', 'POST'])
def download(response):
    """
    Returns Rezdy Marketplace products
    """
    if response.method == 'GET':
        data = requests.get('https://api.rezdy.com/v1/products/marketplace?apiKey=1d7ce4142c634882846e3597aaef36e4')

    return Response(data.json())


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


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

