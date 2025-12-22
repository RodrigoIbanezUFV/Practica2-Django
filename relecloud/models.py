from django.db import models
from django.contrib.auth.models import User

# Definicion de modelos 
class Destination(models.Model):
    name = models.CharField(unique=True, max_length=50)
    description = models.TextField(max_length=2000)
    image = models.ImageField(upload_to='destinations/', null=True, blank=True)

    def __str__(self):
        return self.name


class Cruise(models.Model):
    name = models.CharField(unique=True, max_length=50)
    description = models.TextField(max_length=2000)
    destinations = models.ManyToManyField(Destination, related_name='cruises')

    def __str__(self):
        return self.name


class InfoRequest(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    notes = models.TextField(max_length=2000)
    cruise = models.ForeignKey(Cruise, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name} - {self.cruise.name}"


class Opinion(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    cruise = models.ForeignKey(
        'Cruise',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='opinions'
    )
    destination = models.ForeignKey(
        'Destination',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='opinions'
    )
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)

    def __str__(self):
        target = None
        if self.destination:
            target = self.destination.name
        elif self.cruise:
            target = self.cruise.name
        else:
            target = "Unknown"
        return f"{target} - {self.rating}/5"


class UserTravelRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    destination = models.ForeignKey('Destination', null=True, blank=True, on_delete=models.CASCADE)
    cruise = models.ForeignKey('Cruise', null=True, blank=True, on_delete=models.CASCADE)
    travel_date = models.DateField()

    def __str__(self):
        target = self.destination.name if self.destination else (self.cruise.name if self.cruise else "Unknown")
        return f"{self.user.username} - {target} ({self.travel_date})"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    es_cliente = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
