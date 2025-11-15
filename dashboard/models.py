from django.db import models
from django.contrib.auth.models import User

class FitnessData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    weight = models.FloatField()          # in kilograms
    height = models.FloatField()          # in meters
    steps = models.IntegerField(default=0)
    calories_burned = models.FloatField(default=0)
    bmi = models.FloatField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.height > 0:  # prevent division by zero
            self.bmi = round(self.weight / (self.height ** 2), 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.date}"
