from django.contrib import admin
from .models import Company, QuoteRequest


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'rating', 'is_verified', 'owner')
    list_filter = ('is_verified', 'city')
    list_editable = ('is_verified',)


@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'company', 'reference', 'estimated_cost',
                    'company_quote', 'created_at')