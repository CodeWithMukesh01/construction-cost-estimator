
from django.db import models

class CostRate(models.Model):
    FINISH = [('basic', 'Basic'), ('standard', 'Standard'), ('premium', 'Premium')]
    item = models.CharField(max_length=100)
    finish_level = models.CharField(max_length=20, choices=FINISH)
    rate_per_sqft = models.DecimalField(max_digits=8, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('item', 'finish_level')
        ordering = ['item', 'finish_level']

    def __str__(self):
        return f"{self.item} ({self.finish_level}): ₹{self.rate_per_sqft}/sqft"


class EstimateLog(models.Model):
    plot_size = models.FloatField()
    floors = models.PositiveSmallIntegerField()
    finish_level = models.CharField(max_length=20)
    total = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.plot_size:g} sq ft, {self.floors} fl, {self.finish_level}"    