from rest_framework import serializers

from src.domain.value_objects.biometrics import BiometricType
from src.domain.entities.citoyen import Citoyen
from src.models import User

class EnrollmentSerializer(serializers.Serializer):
    email = serializers.EmailField()
    mot_de_passe = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    nom = serializers.CharField()
    postnom = serializers.CharField()
    prenom = serializers.CharField()
    sexe = serializers.ChoiceField(choices=['M', 'F'])
    date_naissance = serializers.DateField()
    # Champs descriptifs optionnels
    province_origine = serializers.CharField(required=False)
    territoire_origine = serializers.CharField(required=False)
    secteur_origine = serializers.CharField(required=False)
    nom_du_pere = serializers.CharField()
    nom_de_la_mere = serializers.CharField()
    telephone = serializers.CharField(required=False)
    adresse_province = serializers.CharField(required=False, allow_blank=True)
    adresse_commune = serializers.CharField(required=False, allow_blank=True)
    adresse_quartier = serializers.CharField(required=False, allow_blank=True)
    adresse_avenue = serializers.CharField(required=False, allow_blank=True)
    adresse_numero = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if data['mot_de_passe'] != data['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return data

    def to_domain(self) -> Citoyen:
        try:
            return Citoyen.from_request(self.validated_data)
        except ValueError as e:
            raise serializers.ValidationError(str(e))

class EnrollmentCompleteSerializer(EnrollmentSerializer):
    # On ajoute ce que BiometricEnrollSerializer demandait
    biometric_image = serializers.CharField() 
    biometric_type = serializers.ChoiceField(choices=[t.value for t in BiometricType], default="face")
        
class CitoyenProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'nin', 'email', 'nom', 'postnom', 'prenom', 'full_name', 
            'age', 'province_origine', 'territoire_origine', 'secteur_origine','nom_du_pere', 'nom_de_la_mere', 'date_naissance','telephone', 'adresse_province', 'adresse_commune', 'adresse_quartier', 'adresse_avenue', 'adresse_numero'
        ]

    def get_full_name(self, obj):
        return f"{obj.prenom} {obj.nom} {obj.postnom}".upper()

    def get_age(self, obj):
        from src.shared.utils.date_utils import calculate_age
        return calculate_age(obj.date_naissance)