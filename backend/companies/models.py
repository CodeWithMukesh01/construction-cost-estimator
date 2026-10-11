from django.db import models
from django.conf import settings


class Company(models.Model):
    name = models.CharField(max_length=150)
    city = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    years_experience = models.PositiveIntegerField(default=0)
    projects_completed = models.PositiveIntegerField(default=0)
    phone = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=True, blank=True, related_name='company'
    ) 

    class Meta:
        verbose_name_plural = 'companies'
        ordering = ['-rating']

    def __str__(self):
        return self.name


class QuoteRequest(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='quote_requests')
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    customer_email = models.EmailField(blank=True)
    message = models.TextField(blank=True)
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)
    company_quote = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)
    company_note = models.TextField(blank=True)
    reference = models.CharField(max_length=12, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} → {self.company.name}"

   