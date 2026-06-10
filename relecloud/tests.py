from django.test import TestCase
from django.urls import reverse
from django.core import mail
from django.contrib.auth.models import User

from .models import Cruise, InfoRequest, Destination, Opinion, UserTravelRecord
from datetime import date


class InfoRequestViewTests(TestCase):
    def test_info_request_page_loads(self):
        url = reverse("info_request")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Request Information")

    def test_post_valid_info_request_creates_record(self):
        """
        PT1 - TDD (RED expected initially)
        Un POST válido debe crear un registro InfoRequest en la base de datos.
        """
        cruise = Cruise.objects.create(name="Test Cruise")

        url = reverse("info_request")
        payload = {
            "name": "Cristina",
            "email": "nagamose18@gmail.com",
            "cruise": cruise.id,
            "notes": "Please send me more details.",
        }

        response = self.client.post(url, data=payload)

        self.assertEqual(InfoRequest.objects.count(), 1)

        info = InfoRequest.objects.first()
        self.assertEqual(info.name, "Cristina")
        self.assertEqual(info.email, "nagamose18@gmail.com")
        self.assertEqual(info.cruise_id, cruise.id)

    def test_post_valid_info_request_sends_email(self):
        """
        PT1 - TDD
        Un POST válido debe enviar un email al recibir la solicitud.
        """
        cruise = Cruise.objects.create(name="Test Cruise")

        url = reverse("info_request")
        payload = {
            "name": "Cristina",
            "email": "nagamose18@gmail.com",
            "cruise": cruise.id,
            "notes": "Please send me more details.",
        }

        self.client.post(url, data=payload)

        # Deben haberse enviado 2 emails: notificación al admin y confirmación al usuario
        self.assertEqual(len(mail.outbox), 2)

        # El primer correo es la notificación al administrador
        email_admin = mail.outbox[0]
        self.assertIn("Cristina", email_admin.body)
        self.assertIn("nagamose18@gmail.com", email_admin.body)
        self.assertIn("Test Cruise", email_admin.body)

        # El segundo correo es la confirmación al usuario
        email_user = mail.outbox[1]
        self.assertEqual(email_user.to, ["nagamose18@gmail.com"])
        self.assertIn("Cristina", email_user.body)

class DestinationImageTests(TestCase):
    """
    PT2 - Pruebas funcionales de la imagen por destino.
    """

    def test_destination_has_image_field(self):
        """El modelo Destination debe tener un campo de imagen."""
        campos = [f.name for f in Destination._meta.get_fields()]
        self.assertIn("image", campos)

    def test_destination_image_is_optional(self):
        """El campo image debe ser opcional (permite destinos sin imagen propia)."""
        campo_image = Destination._meta.get_field("image")
        self.assertTrue(campo_image.null)
        self.assertTrue(campo_image.blank)

    def test_destination_without_image_has_no_file(self):
        """Un destino creado sin imagen no tiene archivo asociado."""
        destino = Destination.objects.create(
            name="Destino sin foto",
            description="Un destino de prueba sin imagen propia.",
        )
        self.assertFalse(destino.image)

    def test_destinations_page_shows_default_image_when_missing(self):
        """La página de destinos carga y muestra la imagen por defecto si falta la propia."""
        Destination.objects.create(
            name="Destino sin foto",
            description="Destino de prueba.",
        )
        url = reverse("destinations")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "default.jpg")



class AllauthAuthenticationTests(TestCase):
    
    def test_signup_page_uses_allauth(self):
        response = self.client.get("/accounts/signup/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Crear cuenta")

    def test_login_page_uses_allauth(self):
        response = self.client.get("/accounts/login/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Iniciar sesión")

    def test_user_can_signup(self):
        response = self.client.post(
            "/accounts/signup/",
            {
                "username": "usuario_prueba",
                "password1": "PasswordSegura123",
                "password2": "PasswordSegura123",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username="usuario_prueba").exists())

    def test_user_can_login(self):
        User.objects.create_user(
            username="usuario_test",
            password="PasswordSegura123"
        )

        response = self.client.post(
            "/accounts/login/",
            {
                "login": "usuario_test",
                "password": "PasswordSegura123",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_authenticated)

    def test_home_page_shows_login_link(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Log In")

    def test_home_page_shows_signup_link(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sign Up")

class OpinionReviewTests(TestCase):
    """
    PT3 - Pruebas de reviews: solo usuarios con viaje registrado pueden opinar.
    """

    def setUp(self):
        self.comprador = User.objects.create_user(username="comprador", password="Pass12345")
        self.sin_compra = User.objects.create_user(username="sincompra", password="Pass12345")
        self.destino = Destination.objects.create(
            name="Marte Test",
            description="Destino de prueba para reviews.",
        )
        # El comprador tiene un viaje registrado a ese destino
        UserTravelRecord.objects.create(
            user=self.comprador,
            destination=self.destino,
            travel_date=date(2025, 1, 1),
        )

    def test_anonimo_es_redirigido_al_login(self):
        """Un usuario no autenticado no puede acceder al formulario de opinión."""
        url = reverse("opinion_create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_usuario_con_viaje_puede_opinar(self):
        """Un usuario con UserTravelRecord puede crear una opinión sobre ese destino."""
        self.client.login(username="comprador", password="Pass12345")
        url = reverse("opinion_create")
        response = self.client.post(url, {
            "choice": "destination",
            "destination": self.destino.id,
            "rating": 5,
        })
        # La opinión se guarda y redirige a destinations
        self.assertEqual(Opinion.objects.count(), 1)
        opinion = Opinion.objects.first()
        self.assertEqual(opinion.destination_id, self.destino.id)
        self.assertEqual(opinion.rating, 5)

    def test_usuario_sin_viaje_no_puede_opinar(self):
        """Un usuario sin UserTravelRecord no puede crear opinión (el form no le ofrece el destino)."""
        self.client.login(username="sincompra", password="Pass12345")
        url = reverse("opinion_create")
        response = self.client.post(url, {
            "choice": "destination",
            "destination": self.destino.id,
            "rating": 5,
        })
        # No se crea ninguna opinión (el destino no está en su queryset permitido)
        self.assertEqual(Opinion.objects.count(), 0)

    def test_valoracion_media_se_calcula(self):
        """La valoración media de un destino se calcula a partir de sus opiniones."""
        from django.db.models import Avg
        otro = User.objects.create_user(username="otro", password="Pass12345")
        UserTravelRecord.objects.create(
            user=otro, destination=self.destino, travel_date=date(2025, 1, 2)
        )
        Opinion.objects.create(destination=self.destino, rating=5)
        Opinion.objects.create(destination=self.destino, rating=3)
        media = Opinion.objects.filter(destination=self.destino).aggregate(avg=Avg("rating"))["avg"]
        self.assertEqual(media, 4.0)

class PopularityOrderingTests(TestCase):
    """
    PT4 - Prueba funcional del orden de destinos por popularidad.
    """

    def test_destinations_ordered_by_popularity(self):
        """
        Los destinos se ordenan por número de reviews (desc) y luego por media (desc).
        El destino con más reviews debe aparecer antes que uno con menos.
        """
        # Destino A: 2 reviews
        destino_a = Destination.objects.create(name="Destino A", description="desc A")
        Opinion.objects.create(destination=destino_a, rating=3)
        Opinion.objects.create(destination=destino_a, rating=5)

        # Destino B: 1 review
        destino_b = Destination.objects.create(name="Destino B", description="desc B")
        Opinion.objects.create(destination=destino_b, rating=5)

        # Destino C: 0 reviews
        destino_c = Destination.objects.create(name="Destino C", description="desc C")

        url = reverse("destinations")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # La vista pasa los destinos en orden en el contexto
        destinos = list(response.context["destinations"])

        # A (2 reviews) antes que B (1 review) antes que C (0 reviews)
        self.assertEqual(destinos[0], destino_a)
        self.assertEqual(destinos[1], destino_b)
        self.assertEqual(destinos[2], destino_c)

    def test_tiebreak_by_average_rating(self):
        """
        A igualdad de número de reviews, el de mayor media va primero.
        """
        # Ambos con 1 review, pero distinta nota
        destino_alto = Destination.objects.create(name="Nota Alta", description="desc")
        Opinion.objects.create(destination=destino_alto, rating=5)

        destino_bajo = Destination.objects.create(name="Nota Baja", description="desc")
        Opinion.objects.create(destination=destino_bajo, rating=1)

        url = reverse("destinations")
        response = self.client.get(url)
        destinos = list(response.context["destinations"])

        # El de nota 5 va antes que el de nota 1 (mismo nº de reviews)
        self.assertLess(
            destinos.index(destino_alto),
            destinos.index(destino_bajo),
        )