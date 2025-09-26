from rest_framework import serializers
from django.contrib.auth.models import User
from .models import RiskEvent, SupplierKPI, AnomalyDetection, RiskMitigation


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class RiskEventSerializer(serializers.ModelSerializer):
    """Serializer for RiskEvent model"""
    
    reported_by = UserSerializer(read_only=True)
    risk_type_display = serializers.CharField(source='get_risk_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    mitigation_count = serializers.SerializerMethodField()
    
    class Meta:
        model = RiskEvent
        fields = [
            'id', 'title', 'description', 'risk_type', 'risk_type_display',
            'severity', 'severity_display', 'status', 'status_display',
            'probability', 'impact_score', 'risk_score', 'supplier_id',
            'order_id', 'product_id', 'detected_at', 'reported_by',
            'created_at', 'updated_at', 'metadata', 'mitigation_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'reported_by']
    
    def get_mitigation_count(self, obj):
        """Get count of mitigation actions for this risk event"""
        return obj.mitigations.count()
    
    def validate_probability(self, value):
        """Validate probability is between 0 and 1"""
        if not 0.0 <= value <= 1.0:
            raise serializers.ValidationError("Probability must be between 0.0 and 1.0")
        return value
    
    def validate_impact_score(self, value):
        """Validate impact score is between 0 and 10"""
        if not 0.0 <= value <= 10.0:
            raise serializers.ValidationError("Impact score must be between 0.0 and 10.0")
        return value


class RiskEventCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating RiskEvent instances"""
    
    class Meta:
        model = RiskEvent
        fields = [
            'title', 'description', 'risk_type', 'severity', 'status',
            'probability', 'impact_score', 'supplier_id', 'order_id',
            'product_id', 'detected_at', 'metadata'
        ]
    
    def validate_probability(self, value):
        """Validate probability is between 0 and 1"""
        if not 0.0 <= value <= 1.0:
            raise serializers.ValidationError("Probability must be between 0.0 and 1.0")
        return value
    
    def validate_impact_score(self, value):
        """Validate impact score is between 0 and 10"""
        if not 0.0 <= value <= 10.0:
            raise serializers.ValidationError("Impact score must be between 0.0 and 10.0")
        return value


class RiskMitigationSerializer(serializers.ModelSerializer):
    """Serializer for RiskMitigation model"""
    
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = RiskMitigation
        fields = [
            'id', 'risk_event', 'action_type', 'action_type_display',
            'title', 'description', 'status', 'status_display',
            'assigned_to', 'assigned_to_id', 'due_date', 'completed_date',
            'estimated_cost', 'actual_cost', 'effectiveness_score',
            'created_at', 'updated_at', 'metadata'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_effectiveness_score(self, value):
        """Validate effectiveness score is between 0 and 10"""
        if value is not None and not 0.0 <= value <= 10.0:
            raise serializers.ValidationError("Effectiveness score must be between 0.0 and 10.0")
        return value


class SupplierKPISerializer(serializers.ModelSerializer):
    """Serializer for SupplierKPI model"""
    
    kpi_type_display = serializers.CharField(source='get_kpi_type_display', read_only=True)
    performance_status = serializers.SerializerMethodField()
    
    class Meta:
        model = SupplierKPI
        fields = [
            'id', 'supplier_id', 'kpi_type', 'kpi_type_display',
            'value', 'target_value', 'unit', 'period_start', 'period_end',
            'performance_ratio', 'trend', 'performance_status',
            'created_at', 'updated_at', 'metadata'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'performance_ratio']
    
    def get_performance_status(self, obj):
        """Get performance status based on ratio to target"""
        if obj.performance_ratio is None:
            return None
        
        if obj.performance_ratio >= 1.0:
            return 'excellent'
        elif obj.performance_ratio >= 0.8:
            return 'good'
        elif obj.performance_ratio >= 0.6:
            return 'satisfactory'
        else:
            return 'needs_improvement'
    
    def validate(self, data):
        """Validate period dates"""
        if data['period_start'] >= data['period_end']:
            raise serializers.ValidationError("Period start must be before period end")
        return data


class AnomalyDetectionSerializer(serializers.ModelSerializer):
    """Serializer for AnomalyDetection model"""
    
    anomaly_type_display = serializers.CharField(source='get_anomaly_type_display', read_only=True)
    confidence_level_display = serializers.CharField(source='get_confidence_level_display', read_only=True)
    severity_indicator = serializers.SerializerMethodField()
    
    class Meta:
        model = AnomalyDetection
        fields = [
            'id', 'anomaly_type', 'anomaly_type_display',
            'confidence_level', 'confidence_level_display', 'confidence_score',
            'entity_type', 'entity_id', 'feature_name',
            'actual_value', 'expected_value', 'deviation_percentage',
            'detected_at', 'period_start', 'period_end',
            'is_investigated', 'investigation_notes', 'is_false_positive',
            'severity_indicator', 'created_at', 'updated_at', 'metadata'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_severity_indicator(self, obj):
        """Get severity indicator based on confidence and deviation"""
        if obj.confidence_score >= 0.9 and abs(obj.deviation_percentage) >= 50:
            return 'critical'
        elif obj.confidence_score >= 0.8 and abs(obj.deviation_percentage) >= 30:
            return 'high'
        elif obj.confidence_score >= 0.7 and abs(obj.deviation_percentage) >= 15:
            return 'medium'
        else:
            return 'low'
    
    def validate_confidence_score(self, value):
        """Validate confidence score is between 0 and 1"""
        if not 0.0 <= value <= 1.0:
            raise serializers.ValidationError("Confidence score must be between 0.0 and 1.0")
        return value
    
    def validate(self, data):
        """Validate period dates"""
        if data['period_start'] >= data['period_end']:
            raise serializers.ValidationError("Period start must be before period end")
        return data


class RiskScoreSerializer(serializers.Serializer):
    """Serializer for risk scoring requests"""
    
    entity_type = serializers.ChoiceField(
        choices=['supplier', 'product', 'order', 'category'],
        required=True
    )
    entity_id = serializers.CharField(max_length=100, required=True)
    time_horizon = serializers.ChoiceField(
        choices=['7d', '30d', '90d', '180d', '365d'],
        default='30d'
    )
    risk_types = serializers.ListField(
        child=serializers.ChoiceField(choices=RiskEvent.RISK_TYPES),
        required=False,
        allow_empty=True
    )
    include_historical = serializers.BooleanField(default=True)
    
    class Meta:
        fields = ['entity_type', 'entity_id', 'time_horizon', 'risk_types', 'include_historical']


class AnalyticsQuerySerializer(serializers.Serializer):
    """Serializer for analytics query requests"""
    
    metric = serializers.ChoiceField(
        choices=[
            'risk_events_count', 'risk_score_avg', 'supplier_performance',
            'anomaly_detection_count', 'mitigation_effectiveness',
            'trend_analysis', 'risk_distribution'
        ],
        required=True
    )
    entity_type = serializers.ChoiceField(
        choices=['supplier', 'product', 'order', 'category', 'global'],
        default='global'
    )
    entity_id = serializers.CharField(max_length=100, required=False, allow_blank=True)
    time_period = serializers.ChoiceField(
        choices=['7d', '30d', '90d', '180d', '365d', 'all'],
        default='30d'
    )
    aggregation = serializers.ChoiceField(
        choices=['day', 'week', 'month', 'quarter'],
        default='day'
    )
    filters = serializers.JSONField(required=False, default=dict)
    
    class Meta:
        fields = ['metric', 'entity_type', 'entity_id', 'time_period', 'aggregation', 'filters']


class RiskDashboardSerializer(serializers.Serializer):
    """Serializer for risk dashboard data"""
    
    total_risk_events = serializers.IntegerField()
    high_severity_events = serializers.IntegerField()
    critical_anomalies = serializers.IntegerField()
    active_mitigations = serializers.IntegerField()
    avg_risk_score = serializers.FloatField()
    risk_trend = serializers.CharField()
    top_risk_suppliers = serializers.ListField()
    recent_events = RiskEventSerializer(many=True)
    kpi_summary = serializers.JSONField()
    
    class Meta:
        fields = [
            'total_risk_events', 'high_severity_events', 'critical_anomalies',
            'active_mitigations', 'avg_risk_score', 'risk_trend',
            'top_risk_suppliers', 'recent_events', 'kpi_summary'
        ]
