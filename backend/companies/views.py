from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Company, QuoteRequest
from .models import Company, QuoteRequest
from .serializers import (CompanySerializer, QuoteRequestSerializer,
                          CompanyRegisterSerializer, CompanyQuoteRequestSerializer,
                          BulkQuoteRequestSerializer)


class CompanyList(generics.ListAPIView):
    serializer_class = CompanySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Company.objects.filter(is_verified=True)
        city = self.request.query_params.get('city')
        if city:
            qs = qs.filter(city__icontains=city)
        return qs


class QuoteRequestCreate(generics.CreateAPIView):
    queryset = QuoteRequest.objects.all()
    serializer_class = QuoteRequestSerializer
    permission_classes = [AllowAny]


class CompanyRegister(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = CompanyRegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(
            {'message': 'Registered. An admin will verify your company before it is listed.'},
            status=status.HTTP_201_CREATED,
        )


class CompanyLogin(ObtainAuthToken):
    """POST username + password -> returns a token."""
    def post(self, request, *args, **kwargs):
        ser = self.serializer_class(data=request.data, context={'request': request})
        ser.is_valid(raise_exception=True)
        user = ser.validated_data['user']
        if not hasattr(user, 'company'):
            return Response({'error': 'This account is not a company account.'}, status=400)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'company': user.company.name,
            'is_verified': user.company.is_verified,
        })


class MyQuoteRequests(generics.ListAPIView):
    """Quote requests received by the logged-in company only."""
    serializer_class = CompanyQuoteRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        company = getattr(self.request.user, 'company', None)
        if company is None:
            return QuoteRequest.objects.none()
        return QuoteRequest.objects.filter(company=company).order_by('-created_at')


class MyQuoteRequestUpdate(generics.UpdateAPIView):
    """Company submits its quote amount and note (Part B)."""
    serializer_class = CompanyQuoteRequestSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch']

    def get_queryset(self):
        company = getattr(self.request.user, 'company', None)
        if company is None:
            return QuoteRequest.objects.none()
        return QuoteRequest.objects.filter(company=company)

class BulkQuoteRequestCreate(APIView):
    """Customer sends one project to several companies; gets a reference code."""
    permission_classes = [AllowAny]

    def post(self, request):
        ser = BulkQuoteRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ref, count = ser.save()
        return Response({'reference': ref, 'count': count}, status=status.HTTP_201_CREATED)


class CompareQuotes(APIView):
    """Needs BOTH the reference code and the phone number used in the request."""
    permission_classes = [AllowAny]

    def get(self, request):
        ref = request.query_params.get('ref', '').strip().upper()
        phone = request.query_params.get('phone', '').strip()
        if not ref or not phone:
            return Response({'error': 'Enter your reference code and phone number.'}, status=400)

        qs = QuoteRequest.objects.filter(
            reference=ref, customer_phone=phone).select_related('company')
        if not qs.exists():
            return Response({'error': 'No requests found. Check the code and phone number.'},
                            status=404)

        data = []
        for q in qs:
            data.append({
                'company': q.company.name,
                'city': q.company.city,
                'rating': float(q.company.rating),
                'years_experience': q.company.years_experience,
                'projects_completed': q.company.projects_completed,
                'company_phone': q.company.phone if q.company_quote else '',
                'your_estimate': int(q.estimated_cost) if q.estimated_cost else None,
                'company_quote': int(q.company_quote) if q.company_quote else None,
                'company_note': q.company_note,
            })
        # quoted companies first, cheapest first; waiting ones last
        data.sort(key=lambda d: (d['company_quote'] is None, d['company_quote'] or 0))
        return Response(data)    