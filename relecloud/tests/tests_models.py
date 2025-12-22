from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

class Destination(models.Model):
    name = models.CharField(
        unique=True,
        max_length=50,
        null=False,
        blank=False,
    )
    description = models.TextField(
        max_length=2000,
        null=False,
        blank=False
    )
    image = models.ImageField(
        upload_to='destinations/',
        default='destinations/default.jpg',
        null=False,
        blank=False
    )
    def _str_(self):
        return self.name
    
    # Método get_absolute_url para redirigir a la vista de detalle del destino
    def get_absolute_url(self):
        return reverse('destination_detail', args=[str(self.pk)])

class Cruise(models.Model):
    name = models.CharField(
        unique=True,
        max_length=50,
        null=False,
        blank=False,
    )
    description = models.TextField(
        max_length=2000,
        null=False,
        blank=False
    )
    destinations = models.ManyToManyField(
        Destination,
        related_name='cruises'
    )
    def _str_(self):
        return self.name

class InfoRequest(models.Model):
    name = models.CharField(
        max_length=50,
        null=False,
        blank=False,
    )
    email = models.EmailField()
    notes = models.TextField(
        max_length=2000,
        null=False,
        blank=False
    )
    cruise = models.ForeignKey(
        Cruise,
        on_delete=models.PROTECT
    )

class Opinion(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    cruise = models.ForeignKey('Cruise', on_delete=models.CASCADE, null=True, blank=True)
    destination = models.ForeignKey('Destination', on_delete=models.CASCADE, null=True, blank=True, related_name='opinions')  # Aquí se añade related_name
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)

    def _str_(self):
        return f"Rating: {self.rating}"
    

class UserTravelRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    destination = models.ForeignKey('Destination', null=True, blank=True, on_delete=models.CASCADE)
    cruise = models.ForeignKey('Cruise', null=True, blank=True, on_delete=models.CASCADE)
    travel_date = models.DateField()

    def _str_(self):
        # Aquí se pueden hacer las importaciones solo cuando sean necesarias
        from models import Destination, Cruise  # Importación local
        return f"{self.user.username} - {self.destination.name if self.destination else self.cruise.name} ({self.travel_date})"
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    es_cliente = models.BooleanField(default=False)

def _str_(self):
    return self.user.username