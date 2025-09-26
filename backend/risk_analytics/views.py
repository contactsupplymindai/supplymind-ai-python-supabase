from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import timedelta

from .models import RiskEvent, SupplierKPI, AnomalyDetection, RiskMitigation
from .serializers import (
    RiskEventSerializer,
    RiskEventCreateSerializer,
    SupplierKPISerializer,
    AnomalyDetectionSerializer,
    RiskMitigationSerializer,
    RiskScoreSerializer,
    AnalyticsQuerySerializer,
    RiskDashboardSerializer,
)


class RiskEventViewSet(viewsets.ModelViewSet):
    queryset = RiskEvent.objects.all()
    serializer_class = RiskEventSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create']:
            return RiskEventCreateSerializer
        return RiskEventSerializer

    def perform_create(self, serializer):
        instance = serializer.save(reported_by=self.request.user)
        return instance

    @action(detail=False, methods=['post'], url_path='score')
    def score(self, request):
        serializer = RiskScoreSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Simple risk scoring algorithm (placeholder)
        base_score = 0.0
        qs = RiskEvent.objects.all()
        if data['entity_type'] != 'global':
            field = f"{data['entity_type']}_id"
            qs = qs.filter(**{field: data['entity_id']})
        if data.get('risk_types'):
            qs = qs.filter(risk_type__in=[r[0] if isinstance(r, tuple) else r for r in data['risk_types']])

        avg_score = qs.aggregate(avg=Avg('risk_score'))['avg'] or 0.0
        count = qs.count()
        # Combine average score with event volume factor
        score = min(100.0, (avg_score * 10.0) + (count ** 0.5) * 5)

        return Response({
            'entity_type': data['entity_type'],
            'entity_id': data['entity_id'],
            'score': round(score, 2),
            'avg_event_risk_score': round(avg_score, 2),
            'events_count': count,
        })

    @action(detail=False, methods=['get'], url_path='recent')
    def recent(self, request):
        limit = int(request.query_params.get('limit', 20))
        queryset = self.get_queryset().order_by('-created_at')[:limit]
        return Response(RiskEventSerializer(queryset, many=True).data)


class RiskMitigationViewSet(viewsets.ModelViewSet):
    queryset = RiskMitigation.objects.all()
    serializer_class = RiskMitigationSerializer
    permission_classes = [IsAuthenticated]


class SupplierKPIViewSet(viewsets.ModelViewSet):
    queryset = SupplierKPI.objects.all()
    serializer_class = SupplierKPISerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        supplier_id = request.query_params.get('supplier_id')
        qs = self.get_queryset()
        if supplier_id:
            qs = qs.filter(supplier_id=supplier_id)

        # Aggregate latest KPI per type
        latest = {}
        for kpi in qs.order_by('supplier_id', 'kpi_type', '-period_end'):
            key = (kpi.supplier_id, kpi.kpi_type)
            if key not in latest:
                latest[key] = SupplierKPISerializer(kpi).data
        return Response({'items': list(latest.values())})


class AnomalyDetectionViewSet(viewsets.ModelViewSet):
    queryset = AnomalyDetection.objects.all()
    serializer_class = AnomalyDetectionSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='critical')
        
    def critical(self, request):
        qs = self.get_queryset().filter(confidence_level__in=['HIGH','VERY_HIGH'])
        return Response(self.serializer_class(qs, many=True).data)


class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='query')
    def query(self, request):
        serializer = AnalyticsQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data

        now = timezone.now()
        period_map = {
            '7d': now - timedelta(days=7),
            '30d': now - timedelta(days=30),
            '90d': now - timedelta(days=90),
            '180d': now - timedelta(days=180),
            '365d': now - timedelta(days=365),
            'all': None,
        }
        since = period_map.get(params['time_period'])

        # Build filters
        risk_qs = RiskEvent.objects.all()
        anomaly_qs = AnomalyDetection.objects.all()
        kpi_qs = SupplierKPI.objects.all()

        if since:
            risk_qs = risk_qs.filter(created_at__gte=since)
            anomaly_qs = anomaly_qs.filter(detected_at__gte=since)
            kpi_qs = kpi_qs.filter(period_end__gte=since)

        if params['entity_type'] != 'global' and params.get('entity_id'):
            field = f"{params['entity_type']}_id"
            risk_qs = risk_qs.filter(**{field: params['entity_id']})
            anomaly_qs = anomaly_qs.filter(entity_type=params['entity_type'], entity_id=params['entity_id'])
            if params['entity_type'] == 'supplier':
                kpi_qs = kpi_qs.filter(supplier_id=params['entity_id'])

        metric = params['metric']
        result = {}

        if metric == 'risk_events_count':
            result = {
                'count': risk_qs.count(),
                'by_severity': dict(risk_qs.values_list('severity').annotate(c=Count('id')).values_list('severity', 'c')),
                'by_type': dict(risk_qs.values_list('risk_type').annotate(c=Count('id')).values_list('risk_type', 'c')),
            }
        elif metric == 'risk_score_avg':
            result = {
                'avg_score': round(risk_qs.aggregate(avg=Avg('risk_score'))['avg'] or 0.0, 2)
            }
        elif metric == 'supplier_performance':
            # Return latest KPI per type for supplier
            latest = {}
            for kpi in kpi_qs.order_by('supplier_id', 'kpi_type', '-period_end'):
                key = (kpi.supplier_id, kpi.kpi_type)
                if key not in latest:
                    latest[key] = SupplierKPISerializer(kpi).data
            result = {'items': list(latest.values())}
        elif metric == 'anomaly_detection_count':
            result = {
                'count': anomaly_qs.count(),
                'by_type': dict(anomaly_qs.values_list('anomaly_type').annotate(c=Count('id')).values_list('anomaly_type', 'c')),
            }
        elif metric == 'mitigation_effectiveness':
            mitigations = RiskMitigation.objects.filter(risk_event__in=risk_qs)
            total = mitigations.count()
            completed = mitigations.filter(status='COMPLETED').count()
            avg_effectiveness = round(mitigations.aggregate(avg=Avg('effectiveness_score'))['avg'] or 0.0, 2)
            result = {
                'total': total,
                'completed': completed,
                'completion_rate': round((completed/total)*100, 2) if total else 0,
                'avg_effectiveness': avg_effectiveness,
            }
        elif metric == 'trend_analysis':
            # Simple time-bucketed counts
            agg = params['aggregation']
            delta = {'day': 1, 'week': 7, 'month': 30, 'quarter': 90}[agg]
            start = since or (now - timedelta(days=180))
            buckets = []
            d = start
            while d <= now:
                next_d = d + timedelta(days=delta)
                buckets.append({
                    'start': d.isoformat(),
                    'end': next_d.isoformat(),
                    'risk_events': risk_qs.filter(created_at__gte=d, created_at__lt=next_d).count(),
                    'anomalies': anomaly_qs.filter(detected_at__gte=d, detected_at__lt=next_d).count(),
                })
                d = next_d
            result = {'buckets': buckets}
        elif metric == 'risk_distribution':
            # Distribution of risk scores
            bins = {'0-2': 0, '2-4': 0, '4-6': 0, '6-8': 0, '8-10': 0}
            for rs in risk_qs.values_list('risk_score', flat=True):
                if rs is None:
                    continue
                if rs < 2:
                    bins['0-2'] += 1
                elif rs < 4:
                    bins['2-4'] += 1
                elif rs < 6:
                    bins['4-6'] += 1
                elif rs < 8:
                    bins['6-8'] += 1
                else:
                    bins['8-10'] += 1
            result = {'bins': bins}
        else:
            return Response({'detail': 'Unknown metric'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(result)

    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        now = timezone.now()
        last_30 = now - timedelta(days=30)

        total_risk = RiskEvent.objects.count()
        high_sev = RiskEvent.objects.filter(severity__in=['HIGH','CRITICAL']).count()
        critical_anom = AnomalyDetection.objects.filter(confidence_level__in=['HIGH','VERY_HIGH']).count()
        active_mit = RiskMitigation.objects.exclude(status__in=['COMPLETED','CANCELLED','CLOSED']).count()
        avg_risk = round(RiskEvent.objects.aggregate(avg=Avg('risk_score'))['avg'] or 0.0, 2)

        recent = RiskEvent.objects.order_by('-created_at')[:10]

        data = {
            'total_risk_events': total_risk,
            'high_severity_events': high_sev,
            'critical_anomalies': critical_anom,
            'active_mitigations': active_mit,
            'avg_risk_score': avg_risk,
            'risk_trend': 'up' if high_sev > (total_risk * 0.2) else 'stable',
            'top_risk_suppliers': list(RiskEvent.objects.values('supplier_id').annotate(avg=Avg('risk_score')).order_by('-avg').values_list('supplier_id', flat=True)[:5]),
            'recent_events': RiskEventSerializer(recent, many=True).data,
            'kpi_summary': {'count': SupplierKPI.objects.filter(period_end__gte=last_30).count()},
        }
        return Response(data)
