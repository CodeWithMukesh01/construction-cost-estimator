from django.contrib import admin
from .models import CostRate

@admin.register(CostRate)
class CostRateAdmin(admin.ModelAdmin):
    list_display = ('item', 'finish_level', 'rate_per_sqft', 'updated_at')
    list_filter = ('finish_level',)