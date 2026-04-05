from rest_framework import serializers

class PartnerVerifyRequestSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    nin = serializers.CharField(required=True)

class PartnerVerifyResponseSerializer(serializers.Serializer):
    nin = serializers.CharField()
    nom = serializers.CharField()
    prenom = serializers.CharField()
    postnom = serializers.CharField(allow_blank=True)
    date_naissance = serializers.DateField(allow_null=True)
    lieu_origine = serializers.CharField(allow_null=True)

class QRCodeRequestSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    nin = serializers.CharField(required=True)

class QRCodeResponseSerializer(serializers.Serializer):
    nin = serializers.CharField()
    qr_code = serializers.CharField()