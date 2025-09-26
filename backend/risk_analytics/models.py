from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class RiskEvent(models.Model):
    """Model for tracking risk events in the supply chain"""
    
    RISK_TYPES = [
        ('SUPPLIER', 'Supplier Risk'),
        ('DEMAND', 'Demand Risk'),
        ('LOGISTICS', 'Logistics Risk'),
        ('FINANCIAL', 'Financial Risk'),
        ('COMPLIANCE', 'Compliance Risk'),
        ('OPERATIONAL', 'Operational Risk'),
        ('ENVIRONMENTAL', 'Environmental Risk'),
    ]
    
    SEVERITY_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('INVESTIGATING', 'Investigating'),
        ('MITIGATING', 'Mitigating'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    risk_type = models.CharField(max_length=20, choices=RISK_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='OPEN')
    probability = models.FloatField(help_text='Probability of occurrence (0.0-1.0)')
    impact_score = models.FloatField(help_text='Impact score (0.0-10.0)')
    risk_score = models.FloatField(help_text='Calculated risk score')
    
    # Associated entities
    supplier_id = models.CharField(max_length=100, blank=True, null=True)
    order_id = models.CharField(max_length=100, blank=True, null=True)
    product_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Metadata
    detected_at = models.DateTimeField(default=timezone.now)
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional context
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at', '-risk_score']
        indexes = [
            models.Index(fields=['risk_type', 'severity']),
            models.Index(fields=['status', 'detected_at']),
            models.Index(fields=['supplier_id']),
            models.Index(fields=['risk_score']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_severity_display()}) - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate risk score if not provided
        if not self.risk_score:
            self.risk_score = self.probability * self.impact_score
        super().save(*args, **kwargs)


class SupplierKPI(models.Model):
    """Model for tracking supplier key performance indicators"""
    
    KPI_TYPES = [
        ('DELIVERY_PERFORMANCE', 'Delivery Performance'),
        ('QUALITY_RATING', 'Quality Rating'),
        ('COST_EFFICIENCY', 'Cost Efficiency'),
        ('RESPONSIVENESS', 'Responsiveness'),
        ('COMPLIANCE_SCORE', 'Compliance Score'),
        ('FINANCIAL_STABILITY', 'Financial Stability'),
        ('INNOVATION_INDEX', 'Innovation Index'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier_id = models.CharField(max_length=100)
    kpi_type = models.CharField(max_length=25, choices=KPI_TYPES)
    value = models.FloatField()
    target_value = models.FloatField(blank=True, null=True)
    unit = models.CharField(max_length=50, default='%')
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Calculated fields
    performance_ratio = models.FloatField(blank=True, null=True)
    trend = models.CharField(max_length=20, blank=True, null=True)  # 'improving', 'declining', 'stable'
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional context
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-period_end', 'supplier_id']
        unique_together = ['supplier_id', 'kpi_type', 'period_start', 'period_end']
        indexes = [
            models.Index(fields=['supplier_id', 'kpi_type']),
            models.Index(fields=['period_start', 'period_end']),
            models.Index(fields=['value']),
        ]
    
    def __str__(self):
        return f"{self.supplier_id} - {self.get_kpi_type_display()}: {self.value}{self.unit}"
    
    def save(self, *args, **kwargs):
        # Calculate performance ratio if target is provided
        if self.target_value and self.target_value > 0:
            self.performance_ratio = self.value / self.target_value
        super().save(*args, **kwargs)


class AnomalyDetection(models.Model):
    """Model for storing anomaly detection results"""
    
    ANOMALY_TYPES = [
        ('DEMAND_SPIKE', 'Demand Spike'),
        ('DEMAND_DROP', 'Demand Drop'),
        ('PRICE_FLUCTUATION', 'Price Fluctuation'),
        ('DELIVERY_DELAY', 'Delivery Delay'),
        ('QUALITY_DEVIATION', 'Quality Deviation'),
        ('SUPPLY_DISRUPTION', 'Supply Disruption'),
        ('PATTERN_CHANGE', 'Pattern Change'),
    ]
    
    CONFIDENCE_LEVELS = [
        ('LOW', 'Low (< 70%)'),
        ('MEDIUM', 'Medium (70-85%)'),
        ('HIGH', 'High (85-95%)'),
        ('VERY_HIGH', 'Very High (> 95%)'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    anomaly_type = models.CharField(max_length=20, choices=ANOMALY_TYPES)
    confidence_level = models.CharField(max_length=10, choices=CONFIDENCE_LEVELS)
    confidence_score = models.FloatField(help_text='Confidence score (0.0-1.0)')
    
    # Data points
    entity_type = models.CharField(max_length=50)  # 'supplier', 'product', 'order', etc.
    entity_id = models.CharField(max_length=100)
    feature_name = models.CharField(max_length=100)
    actual_value = models.FloatField()
    expected_value = models.FloatField()
    deviation_percentage = models.FloatField()
    
    # Time context
    detected_at = models.DateTimeField(default=timezone.now)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Status tracking
    is_investigated = models.BooleanField(default=False)
    investigation_notes = models.TextField(blank=True)
    is_false_positive = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional context
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-detected_at', '-confidence_score']
        indexes = [
            models.Index(fields=['anomaly_type', 'confidence_level']),
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['detected_at']),
            models.Index(fields=['confidence_score']),
        ]
    
    def __str__(self):
        return f"{self.get_anomaly_type_display()} - {self.entity_type}:{self.entity_id} ({self.get_confidence_level_display()})"


class RiskMitigation(models.Model):
    """Model for tracking risk mitigation actions"""
    
    ACTION_TYPES = [
        ('PREVENTIVE', 'Preventive'),
        ('CORRECTIVE', 'Corrective'),
        ('DETECTIVE', 'Detective'),
        ('COMPENSATING', 'Compensating'),
    ]
    
    STATUS_CHOICES = [
        ('PLANNED', 'Planned'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('ON_HOLD', 'On Hold'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    risk_event = models.ForeignKey(RiskEvent, on_delete=models.CASCADE, related_name='mitigations')
    action_type = models.CharField(max_length=15, choices=ACTION_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PLANNED')
    
    # Assignment and timeline
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateTimeField(blank=True, null=True)
    completed_date = models.DateTimeField(blank=True, null=True)
    
    # Effectiveness tracking
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    actual_cost = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    effectiveness_score = models.FloatField(blank=True, null=True, help_text='Effectiveness rating (0.0-10.0)')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional context
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['risk_event', 'status']),
            models.Index(fields=['assigned_to', 'due_date']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
