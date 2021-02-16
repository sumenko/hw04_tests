from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

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
        response = self.guest_client.get(reverse("posts:index"))
        self.assertEqual(response.status_code, 200)

    # проверить доступность в соответствии с правами
    def test_urls_authorized(self):

        cases = [
            (reverse("posts:index"), 200),
            (reverse("posts:group_slug", kwargs={"slug": "non-exists"}), 404),
            (reverse("posts:group_slug", kwargs={"slug": "aviators"}), 200),
            # тут влияет авторизован/нет
            (reverse("posts:new_post"), 200),
            (reverse("posts:profile", kwargs={"username": "johndoe"}), 200),
            (reverse("posts:profile",
                     kwargs={"username": "nonexistsuser"}), 404),
            (reverse("posts:post",
                     kwargs={"username": "johndoe", "post_id": "1"}), 200),
            # не автор, пост не существует
            (reverse("posts:edit_post",
                     kwargs={"username": "myst", "post_id": "1"}), 404),
            # автор, пост существует
            (reverse("posts:edit_post",
                     kwargs={"username": "myst", "post_id": "2"}), 200),
            (reverse("about:author"), 200),
            (reverse("about:tech"), 200),
        ]
        for url, correct_code in cases:
            with self.subTest(value=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, correct_code)

    # обратиться по URL и проверить ожидаемые шаблоны
    def test_urls_anonymous(self):
        url_cases = [
            (reverse("posts:index"), 200),
            (reverse("posts:group_slug", kwargs={"slug": "non-exists"}), 404),
            (reverse("posts:group_slug", kwargs={"slug": "aviators"}), 200),
            # тут влияет авторизован/нет
            (reverse("posts:new_post"), 302),
            (reverse("posts:profile", kwargs={"username": "johndoe"}), 200),
            (reverse("posts:profile",
                     kwargs={"username": "nonexistsuser"}), 404),
            (reverse("posts:post",
                     kwargs={"username": "johndoe", "post_id": "1"}), 200),
            # не авторизован, пост не существует
            (reverse("posts:edit_post",
                     kwargs={"username": "myst", "post_id": "1"}), 302),
            # не авторизован, пост существует
            (reverse("posts:edit_post",
                     kwargs={"username": "myst", "post_id": "2"}), 302),
            (reverse("about:author"), 200),
            (reverse("about:tech"), 200),
        ]
        for url, correct_code in url_cases:
            with self.subTest(value=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, correct_code)

    # редиректы
    def test_new_post_redirect_anonymous(self):
        response = self.guest_client.get(reverse("posts:new_post"),
                                         follow=True)
        self.assertRedirects(response, reverse("login") + "?next=%2Fnew%2F")

    def test_edit_post_redirect_wrong_user(self):
        response = self.authorized_client.get(
            reverse("posts:edit_post",
                    kwargs={"username": "johndoe", "post_id": "1"}),
            follow=True)
        self.assertRedirects(response,
                             reverse("posts:post", kwargs={
                                     "username": "johndoe",
                                     "post_id": "1"}))

    # темплейты для авторизованного и анонимуса
    def test_templates_authorized(self):
        template_cases = [
            (reverse("posts:index"), "index.html"),
            (reverse("posts:group_slug",
                     kwargs={"slug": "aviators"}), "group.html"),
            (reverse("posts:show_groups"), "show_groups.html"),
            (reverse("posts:new_post"), "new_post.html"),
            (reverse("posts:edit_post",
                     kwargs={"username": "myst", "post_id": 2}),
                "new_post.html"),
        ]
        for url, template in template_cases:
            with self.subTest(value=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    # темплейты
    def test_templates_anonymous(self):
        """ Проверка использования шаблонов для анонимного пользователя """
        template_cases = [
            (reverse("posts:index"), "index.html"),
            (reverse("posts:group_slug",
                     kwargs={"slug": "aviators"}), "group.html"),
            (reverse("posts:show_groups"), "show_groups.html"),
        ]
        for url, template in template_cases:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
