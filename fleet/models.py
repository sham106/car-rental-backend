from django.db import models
import json

class Vehicle(models.Model):
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    category = models.CharField(max_length=50)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.TextField(blank=True, null=True)
    gallery = models.TextField(blank=True, default='[]')  # Store as JSON array
    transmission = models.CharField(max_length=50, default='Automatic')
    seats = models.IntegerField(default=2)
    engine = models.CharField(max_length=100, blank=True, null=True)
    horsepower = models.IntegerField(default=0)
    zero_to_sixty = models.CharField(max_length=50, blank=True, null=True)
    top_speed = models.CharField(max_length=50, blank=True, null=True)
    availability = models.CharField(max_length=50, default='Available')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.make} {self.model}"

    def get_gallery_list(self):
        """Return gallery as a list of strings"""
        if not self.gallery:
            return []
        try:
            return json.loads(self.gallery)
        except json.JSONDecodeError:
            return []

    def set_gallery_list(self, gallery_list):
        """Set gallery from a list of strings"""
        self.gallery = json.dumps(gallery_list)