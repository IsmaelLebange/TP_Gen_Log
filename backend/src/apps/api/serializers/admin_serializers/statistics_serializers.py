from rest_framework import serializers

class StatisticsSerializer(serializers.Serializer):
    total_citoyens = serializers.IntegerField()
    total_citoyens_30d = serializers.IntegerField()
    sexe_repartition = serializers.ListField()
    age_repartition = serializers.DictField()
    top_provinces = serializers.ListField()
    enrollments_by_day = serializers.ListField()
    documents_status = serializers.ListField()
    top_validators = serializers.ListField()
    recent_audits = serializers.ListField()