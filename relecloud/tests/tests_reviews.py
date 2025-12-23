# relecloud/tests/test_reviews.py
"""
Tests TDD para PT3 — Reviews vinculadas a Cruise.
Asegúrate de que los names de URL usados aquí ('cruise_detail' y 'cruise_review_create')
coincidan con los declarados en relecloud/urls.py. Si no, cámbialos.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from relecloud import models as rc_models

User = get_user_model()


class ReviewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.buyer = User.objects.create_user(username='buyer', password='pass')
        self.other = User.objects.create_user(username='other', password='pass')

        # Crear Cruise (ajusta campos si tu modelo difiere)
        # Si tu modelo se llama diferente, adapta esta línea.
        self.cruise = rc_models.Cruise.objects.create(name='Cruise A', description='Test cruise')

    def _cruise_detail_url(self):
        return reverse('cruise_detail', args=[self.cruise.id])

    def _cruise_review_create_url(self):
        return reverse('cruise_review_create', args=[self.cruise.id])

    def test_anonymous_redirected_from_review_create(self):
        """Un anónimo no puede acceder a la URL de creación: redirigir a login o devolver 401/403."""
        url = self._cruise_review_create_url()
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (302, 401, 403))
        if resp.status_code == 302:
            self.assertIn('login', resp.url.lower())

    def test_user_without_purchase_cannot_see_review_form(self):
        """Un usuario logueado pero sin compra no debe ver el formulario en el detail."""
        self.client.force_login(self.other)
        resp = self.client.get(self._cruise_detail_url())
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, 'name="rating"')

    def test_user_with_purchase_sees_form_and_can_post_review(self):
        """Usuario comprador ve el form y puede enviar review (queda asociada)."""
        if not hasattr(rc_models, 'Purchase') or not hasattr(rc_models, 'Review'):
            self.fail('Models Purchase and/or Review not implemented yet in relecloud.models')

        Purchase = rc_models.Purchase
        Review = rc_models.Review

        # crear Purchase que vincule buyer y cruise
        Purchase.objects.create(user=self.buyer, cruise=self.cruise)
        self.client.force_login(self.buyer)

        # GET detail -> contiene form
        resp = self.client.get(self._cruise_detail_url())
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'name="rating"')

        # POST para crear review
        post_url = self._cruise_review_create_url()
        resp2 = self.client.post(post_url, {'rating': 5, 'comment': 'Great trip'})
        self.assertIn(resp2.status_code, (302, 201, 200, 303))
        self.assertTrue(Review.objects.filter(author=self.buyer, cruise=self.cruise, rating=5).exists())

    def test_prevent_duplicate_review(self):
        """No permitir más de una review por (author, cruise)."""
        if not hasattr(rc_models, 'Purchase') or not hasattr(rc_models, 'Review'):
            self.fail('Models Purchase and/or Review not implemented yet in relecloud.models')

        Purchase = rc_models.Purchase
        Review = rc_models.Review

        Purchase.objects.create(user=self.buyer, cruise=self.cruise)
        self.client.force_login(self.buyer)

        post_url = self._cruise_review_create_url()
        resp1 = self.client.post(post_url, {'rating': 4, 'comment': 'Nice'})
        self.assertIn(resp1.status_code, (302, 201, 200, 303))
        count_after_first = Review.objects.filter(author=self.buyer, cruise=self.cruise).count()
        self.assertEqual(count_after_first, 1)

        # Segundo intento no debe crear un segundo registro
        resp2 = self.client.post(post_url, {'rating': 5, 'comment': 'Second'})
        count_after_second = Review.objects.filter(author=self.buyer, cruise=self.cruise).count()
        self.assertEqual(count_after_second, 1)
        self.assertIn(resp2.status_code, (302, 400, 403, 200, 303))

    def test_average_rating_none_when_no_reviews(self):
        """average_rating debe devolver None cuando no hay reviews."""
        if not hasattr(rc_models, 'Review'):
            self.fail('Review model not implemented yet')

        avg_attr = getattr(self.cruise, 'average_rating', None)
        if callable(avg_attr):
            result = self.cruise.average_rating()
            self.assertIsNone(result)
        else:
            self.assertIsNone(avg_attr)

    def test_average_rating_calculation_multiple_reviews(self):
        """Comprobamos cálculo de promedio correcto con varias reviews."""
        if not hasattr(rc_models, 'Purchase') or not hasattr(rc_models, 'Review'):
            self.fail('Models Purchase and/or Review not implemented yet in relecloud.models')

        Purchase = rc_models.Purchase
        Review = rc_models.Review

        Purchase.objects.create(user=self.buyer, cruise=self.cruise)
        other_user = User.objects.create_user(username='u2', password='p')
        Purchase.objects.create(user=other_user, cruise=self.cruise)

        Review.objects.create(author=self.buyer, cruise=self.cruise, rating=5, comment='Great')
        Review.objects.create(author=other_user, cruise=self.cruise, rating=3, comment='Ok')

        avg_attr = getattr(self.cruise, 'average_rating', None)
        if not avg_attr:
            self.fail('Cruise.average_rating() not implemented')

        avg_value = self.cruise.average_rating() if callable(avg_attr) else avg_attr
        self.assertAlmostEqual(avg_value, 4.0, places=2)
