from django.test import Client, TestCase
from django.urls import reverse


class AboutTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_available(self):
        response_author = self.guest_client.get(reverse("about:author"))
        response_tech = self.guest_client.get(reverse("about:tech"))

        self.assertEqual(response_author.status_code, 200,
                         "about/author недостоупно гостевому пользователю")

        self.assertEqual(response_tech.status_code, 200,
                         "about/tech недостоупно гостевому пользователю")

    def test_about_use_template(self):
        response_author = self.guest_client.get(reverse("about:author"))
        response_tech = self.guest_client.get(reverse("about:tech"))

        self.assertTemplateUsed(response_author, "author.html")
        self.assertTemplateUsed(response_tech, "tech.html")
