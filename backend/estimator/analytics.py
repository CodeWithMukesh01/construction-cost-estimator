from datetime import timedelta

from django.db.models import Avg, Count, Q
from django.db.models.functions import TruncWeek
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from companies.models import Company, QuoteRequest
from .models import EstimateLog


def pct(a, b):
    return round(a / b * 100, 1) if b else None


class StaffLogin(ObtainAuthToken):
    """Admin users only (is_staff). Company accounts cannot use this."""
    def post(self, request, *args, **kwargs):
        ser = self.serializer_class(data=request.data, context={'request': request})
        ser.is_valid(raise_exception=True)
        user = ser.validated_data['user']
        if not user.is_staff:
            return Response({'error': 'Staff access only.'}, status=403)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'username': user.username})


class Analytics(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        now = timezone.now()
        week_ago = now - timedelta(days=7)

        # ---- estimates ----
        est = EstimateLog.objects
        estimates_total = est.count()
        estimates_7d = est.filter(created_at__gte=week_ago).count()

        this_monday = (now - timedelta(days=now.weekday())).date()
        starts = [this_monday - timedelta(weeks=i) for i in range(7, -1, -1)]  # last 8 weeks
        rows = (est.filter(created_at__date__gte=starts[0])
                .annotate(week=TruncWeek('created_at'))
                .values('week').annotate(n=Count('id')))
        by_week = {r['week'].date(): r['n'] for r in rows}
        weekly = [{'week': d.isoformat(), 'count': by_week.get(d, 0)} for d in starts]

        finish_counts = {r['finish_level']: r['n']
                         for r in est.values('finish_level').annotate(n=Count('id'))}
        by_finish = [{'level': lv, 'count': finish_counts.get(lv, 0)}
                     for lv in ('basic', 'standard', 'premium')]
        avg_total = est.aggregate(a=Avg('total'))['a']

        # ---- companies ----
        companies_total = Company.objects.count()
        companies_verified = Company.objects.filter(is_verified=True).count()

        # ---- quote requests ----
        qr = QuoteRequest.objects
        requests_total = qr.count()
        requests_7d = qr.filter(created_at__gte=week_ago).count()
        quoted = qr.filter(company_quote__isnull=False).count()
        # one "project" = one reference code (older rows without a code count singly)
        projects = (qr.exclude(reference='').values('reference').distinct().count()
                    + qr.filter(reference='').count())

        gaps = [
            (float(q) - float(e)) / float(e) * 100
            for q, e in qr.filter(company_quote__isnull=False,
                                  estimated_cost__isnull=False,
                                  estimated_cost__gt=0)
                          .values_list('company_quote', 'estimated_cost')
        ]
        avg_gap = round(sum(gaps) / len(gaps), 1) if gaps else None

        top = (Company.objects
               .annotate(received=Count('quote_requests'),
                         answered=Count('quote_requests',
                                        filter=Q(quote_requests__company_quote__isnull=False)))
               .filter(received__gt=0).order_by('-received')[:5])

        return Response({
            'estimates_total': estimates_total,
            'estimates_7d': estimates_7d,
            'avg_estimate': round(avg_total) if avg_total else None,
            'weekly': weekly,
            'by_finish': by_finish,
            'companies_total': companies_total,
            'companies_verified': companies_verified,
            'companies_pending': companies_total - companies_verified,
            'requests_total': requests_total,
            'requests_7d': requests_7d,
            'projects': projects,
            'quotes_received': quoted,
            'response_rate': pct(quoted, requests_total),
            'avg_quotes_per_project': round(quoted / projects, 1) if projects else None,
            'estimate_to_request_rate': pct(projects, estimates_total),
            'avg_gap_pct': avg_gap,
            'top_companies': [
                {'name': c.name, 'city': c.city, 'received': c.received, 'answered': c.answered}
                for c in top
            ],
        })