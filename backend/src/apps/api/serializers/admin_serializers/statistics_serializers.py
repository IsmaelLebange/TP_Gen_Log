from rest_framework import serializers

class StatisticsSerializer(serializers.Serializer):
    total_citoyens = serializers.IntegerField()
    pending_documents = serializers.IntegerField()
    today_validations = serializers.IntegerField()
    active_agents = serializers.IntegerField()
    admin_count = serializers.IntegerField()
    # Garde les autres champs si tu veux
    total_citoyens_30d = serializers.IntegerField(required=False)
    sexe_repartition = serializers.ListField(required=False)
    age_repartition = serializers.DictField(required=False)
    top_provinces = serializers.ListField(required=False)
    enrollments_by_day = serializers.ListField(required=False)
    documents_status = serializers.ListField(required=False)
    top_validators = serializers.ListField(required=False)
    recent_audits = serializers.ListField(required=False)