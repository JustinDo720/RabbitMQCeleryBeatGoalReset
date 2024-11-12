from django.db import models

# Create your models here.
class Goals(models.Model):

    DURATION_CHOICES = [
        ('emp', ''),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    name = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    duration = models.CharField(max_length=60,choices=DURATION_CHOICES, default='emp')

    def __str__(self):
        return f'{self.name} - {self.completed}'