from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import NutanixObj


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class RezdySerializer(serializers.Serializer):
    data = serializers.JSONField()
    key = serializers.CharField(max_length=50, allow_blank=False)
    url = serializers.URLField(max_length=200)
    created = serializers.DateTimeField()


class NutanixSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=28)
    password = serializers.CharField(max_length=28)
    created = serializers.DateTimeField()

    def create(self, validated_data):
        return NutanixObj(**validated_data)

    def update(selfself, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.password = validated_data.get('password', instance.password)
        instance.created = validated_data.get('created', instance.created)
        instance.save()
        return instance




