from rest_framework import serializers

class OTPRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    purpose = serializers.CharField(default='LOGIN')

class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    purpose = serializers.CharField(default='LOGIN')