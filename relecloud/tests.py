from django.test import TestCase
from django.urls import reverse
from django.core import mail

from .models import Cruise, InfoRequest


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


