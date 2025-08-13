from django.db import models
from django.utils import timezone

class PortfolioItem(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='porfolio/')
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-upload_date']

    def __str__(self):
        return self.title