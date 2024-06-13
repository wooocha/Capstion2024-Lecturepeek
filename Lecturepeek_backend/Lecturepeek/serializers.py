from rest_framework import serializers


class YouTubeSummarySerializer(serializers.Serializer):
    url = serializers.URLField()
