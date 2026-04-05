from rest_framework import serializers

class AuditLogSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user_id = serializers.IntegerField(allow_null=True)
    user_email = serializers.CharField(allow_null=True)
    action = serializers.CharField()
    entity_type = serializers.CharField()
    entity_id = serializers.CharField()
    old_data = serializers.JSONField(allow_null=True)
    new_data = serializers.JSONField(allow_null=True)
    ip_address = serializers.CharField()
    user_agent = serializers.CharField()
    created_at = serializers.DateTimeField()

class AuditFilterSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=False, allow_null=True)
    action = serializers.CharField(required=False, allow_null=True)
    start_date = serializers.DateTimeField(required=False, allow_null=True)
    end_date = serializers.DateTimeField(required=False, allow_null=True)
    hours = serializers.IntegerField(required=False, min_value=1, max_value=168)
    query = serializers.CharField(required=False, allow_null=True)
    limit = serializers.IntegerField(default=100, min_value=1, max_value=1000)