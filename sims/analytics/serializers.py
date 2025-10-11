"""Serializers for analytics API responses."""

from __future__ import annotations

from rest_framework import serializers


class TrendPointSerializer(serializers.Serializer):
    date = serializers.DateField()
    count = serializers.IntegerField()
    approved = serializers.IntegerField()
    avg_score = serializers.FloatField(allow_null=True)
    moving_average = serializers.FloatField(allow_null=True)


class TrendResponseSerializer(serializers.Serializer):
    metric = serializers.CharField()
    window = serializers.IntegerField()
    series = TrendPointSerializer(many=True)


class ComparativeGroupSerializer(serializers.Serializer):
    value = serializers.FloatField()
    total_entries = serializers.IntegerField()
    approved = serializers.IntegerField()
    average_score = serializers.FloatField()


class ComparativeResponseSerializer(serializers.Serializer):
    primary = ComparativeGroupSerializer()
    secondary = ComparativeGroupSerializer()


class PerformanceMetricsSerializer(serializers.Serializer):
    total_entries = serializers.FloatField()
    pending = serializers.FloatField()
    approved = serializers.FloatField()
    approval_rate = serializers.FloatField()
    rejection_rate = serializers.FloatField()
    pending_rate = serializers.FloatField()
    average_review_hours = serializers.FloatField()


__all__ = [
    "TrendPointSerializer",
    "TrendResponseSerializer",
    "ComparativeResponseSerializer",
    "PerformanceMetricsSerializer",
]
