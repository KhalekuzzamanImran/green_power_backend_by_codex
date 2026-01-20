from rest_framework import serializers


class TokenObtainSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class TokenPairSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField(required=False)


class TokenLogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
