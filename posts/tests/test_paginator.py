from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post


class TestPaginator(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create(username="Johndoe")
        for number in range(13):
            # print(f"Create post {number}")
            Post.objects.create(
                text="Тестовая запись {number}",
                author=cls.user
            )

    def setUp(self):
        super().setUp()
        self.client = Client()

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse("index"))

        self.assertEqual(len(response.context.get("page").object_list), 10)

    def test_second_page_contains_three_records(self):
        response = self.client.get(reverse("index") + "/?page=2")

        self.assertEqual(len(response.context.get("page").object_list), 3)
