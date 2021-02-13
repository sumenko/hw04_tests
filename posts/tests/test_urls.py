from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):  # вызывается перед запуском всех test case
        super().setUpClass()
        # наш тестовый пользователь
        cls.user_one = get_user_model().objects.create(username="johndoe")
        cls.user_two = get_user_model().objects.create(username="myst")

        # Создаем группу
        Group.objects.create(
            title="Сообщество",
            slug="aviators",
            description="Мы любим собирать самолёты",
        )
        Post.objects.create(text="Test text from johndoe",
                            author=cls.user_one,
                            group=None)
        Post.objects.create(text="Test text from myst",
                            author=cls.user_two,
                            group=None)

    def setUp(self):  # вызывается перед запуском каждого test case
        # фикстуры: готовим пользователей тут
        self.guest_client = Client()

        self.user = get_user_model().objects.get(username="myst")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_url_exists_homepage(self):
        # Делаем запрос к главной странице и проверяем статус
        response = self.guest_client.get("/")
        self.assertEqual(response.status_code, 200)

    # проверить доступность в соответствии с правами
    def test_urls_authorized(self):

        cases = [
            ("/", 200),
            ("/about/author/", 200),
            ("/about/tech/", 200),
            ("/group/non-exists/", 404),
            ("/group/aviators/", 200),
            ("/new/", 200),
            ("/johndoe/", 200),
            ("/johndoe/1/", 200),
            ("/myst/1/edit/", 404),  # не автор поста, пост не существует
            ("/myst/2/edit/", 200),  # автор поста
            ("/nonexistsuser/", 404),
        ]
        for url, correct_code in cases:
            with self.subTest(value=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, correct_code)

    # обратиться по URL и проверить ожидаемые шаблоны
    def test_urls_anonymous(self):
        url_cases = [
            ("/", 200),
            ("/group/non-exists/", 404),
            ("/group/aviators/", 200),
            ("/about/author/", 200),
            ("/about/tech/", 200),
            ("/new/", 302),
            ("/johndoe/", 200),
            ("/johndoe/1/", 200),
            ("/myst/1/edit/", 302),  # не авторизован, пост не существует
            ("/myst/2/edit/", 302),  # не авторизован, пост существует
            ("/nonexistsuser/", 404),
        ]
        for url, correct_code in url_cases:
            with self.subTest(value=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, correct_code)

    # редиректы
    def test_new_post_redirect_anonymous(self):
        response = self.guest_client.get("/new/", follow=True)
        self.assertRedirects(response, "/auth/login/?next=%2Fnew%2F")

    def test_edit_post_redirect_wrong_user(self):
        response = self.authorized_client.get("/johndoe/1/edit/", follow=True)
        self.assertRedirects(response, "/johndoe/1/")

    # темплейты для авторизованного и анонимуса
    def test_templates_authorized(self):
        template_cases = [
            ("/", "index.html"),
            ("/group/aviators/", "group.html"),
            ("/group/", "show_groups.html"),
            ("/new/", "new_post.html"),
            ("/myst/2/edit/", "new_post.html"),
        ]
        for url, template in template_cases:
            with self.subTest(value=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    # темплейты
    def test_templates_anonymous(self):
        template_cases = [
            ("/", "index.html"),
            ("/group/aviators/", "group.html"),
            ("/group/", "show_groups.html"),
        ]
        for url, template in template_cases:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
