import secrets

from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Company, QuoteRequest


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'city', 'description', 'rating',
                  'years_experience', 'projects_completed']


class QuoteRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteRequest
        fields = ['company', 'customer_name', 'customer_phone',
                  'customer_email', 'message', 'estimated_cost']


class CompanyRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(min_length=6, write_only=True)
    name = serializers.CharField(max_length=150)
    city = serializers.CharField(max_length=80)
    phone = serializers.CharField(max_length=20)
    description = serializers.CharField(required=False, allow_blank=True)
    years_experience = serializers.IntegerField(required=False, min_value=0, default=0)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('This username is taken.')
        return value

    def create(self, data):
        user = User.objects.create_user(username=data['username'], password=data['password'])
        return Company.objects.create(
            owner=user,
            name=data['name'],
            city=data['city'],
            phone=data['phone'],
            description=data.get('description', ''),
            years_experience=data.get('years_experience', 0),
            is_verified=False,
        )


class CompanyQuoteRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteRequest
        fields = ['id', 'customer_name', 'customer_phone', 'customer_email',
                  'message', 'estimated_cost', 'company_quote', 'company_note', 'created_at']
        read_only_fields = ['customer_name', 'customer_phone', 'customer_email',
                            'message', 'estimated_cost', 'created_at']
        extra_kwargs = {'company_quote': {'min_value': 1}}


class BulkQuoteRequestSerializer(serializers.Serializer):
    companies = serializers.ListField(
        child=serializers.IntegerField(), min_length=1, max_length=10)
    customer_name = serializers.CharField(max_length=100)
    customer_phone = serializers.CharField(max_length=20)
    customer_email = serializers.EmailField(required=False, allow_blank=True)
    message = serializers.CharField(required=False, allow_blank=True)
    estimated_cost = serializers.DecimalField(
        max_digits=12, decimal_places=0, required=False, allow_null=True)

    def validate(self, data):
        found = Company.objects.filter(id__in=set(data['companies']), is_verified=True)
        if not found.exists():
            raise serializers.ValidationError('Choose at least one verified company.')
        data['company_objs'] = list(found)
        return data

    def create(self, data):
        ref = secrets.token_hex(4).upper()   # e.g. 9F3A12BC
        for c in data['company_objs']:
            QuoteRequest.objects.create(
                company=c,
                reference=ref,
                customer_name=data['customer_name'],
                customer_phone=data['customer_phone'],
                customer_email=data.get('customer_email', ''),
                 message=data.get('message', ''),
                estimated_cost=data.get('estimated_cost'),
            )
        return ref, len(data['company_objs'])