from time import sleep

from django import forms
from django.contrib.auth import get_user_model
from django.core.paginator import Page
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):  # вызывается перед запуском всех test case
        super().setUpClass()
        # наш тестовый пользователь
        cls.user_one = get_user_model().objects.create(username="johndoe")
        cls.posts_per_page = 10
        # Создаем группу и сразу запомним ссылку для поста
        group_link = Group.objects.create(
            title="Авиаторы",
            slug="aviators",
            description="Собираем самолёты"
        )
        Group.objects.create(
            title="Сообщество2",
            slug="group-two",
        )
        # Создаем несколько постов от пользователя в группу и без группы
        Post.objects.create(
            author=cls.user_one,
            text="Запись в сообществе Авиаторы",
            group=group_link,
        )
        # иногда они пишутся с одним временем и тесты странно ведут себя
        sleep(.01)  # потому ставим задержку
        Post.objects.create(
            author=cls.user_one,
            text="Запись без сообщества",
            group=None
        )
        sleep(.01)
        # это посты для паджинатора, ниже для предыдущих тестов
        for number in range(StaticURLTests.posts_per_page+3):
            Post.objects.create(
                author=cls.user_one,
                text=f"{number} запись",
                group=None
            )
            sleep(.01)

    def setUp(self):  # вызывается перед запуском каждого test case
        # фикстуры: готовим пользователей тут
        self.guest_client = Client()

        # заходим под не автором постов
        self.user = get_user_model().objects.create(username="myst")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        # заходим под автором постов
        self.authorized_client_john = Client()
        self.authorized_client_john.force_login(StaticURLTests.user_one)

        # соберем что выдают страницы для разных сообществ для проверки ниже
        test_urls = [
            ("posts:index", reverse("posts:index")),
            ("aviators", reverse("posts:group_slug",
                                 kwargs={"slug": "aviators"})),
            ("group-two", reverse("posts:group_slug",
                                  kwargs={"slug": "group-two"})),
        ]
        self.contexts = {}

        for group, test_url in test_urls:
            response = self.authorized_client.get(test_url)
            self.contexts[group] = response.context.get("page")

    def test_correct_template_views(self):
        """ Вызываются верные шаблоны по соответствующим им именам """
        view_templates = {
            "index.html": reverse("posts:index"),
            "group.html": reverse("posts:group_slug",
                                  kwargs={"slug": "aviators"}),
            "show_groups.html": reverse("posts:show_groups"),
            "new_post.html": reverse("posts:new_post"),
        }

        for template, reverse_name in view_templates.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_correct_context_index(self):
        """ в котнекст index передается объект Post """
        response = self.authorized_client.get(reverse("posts:index"))
        self.assertIsInstance(response.context.get("page")[0], Post)

    def test_correct_context_group(self):
        """ в котнекст group/slug передаются объекты Post, Group """
        response = self.authorized_client.get(reverse(
            "posts:group_slug",
            kwargs={"slug": "aviators"})
        )
        self.assertIsInstance(response.context.get("page")[0], Post)
        self.assertIsInstance(response.context.get("group"), Group)

    def test_correct_context_new_post(self):
        """ проверка контекста для нового поста """
        response = self.authorized_client.get(reverse("posts:new_post"))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField
        }
        for form_label, expected_instance in form_fields.items():
            with self.subTest(value=form_label):
                field = response.context.get("form").fields.get(form_label)
                self.assertIsInstance(field, expected_instance)

        self.assertTrue(response.context.get("new_post"),
                        "В контекст edit_post передана new_post==True")
        self.assertIsNone(response.context.get("post"))

    def test_correct_context_edit_post(self):
        """ проверка контекста для редактируемого поста """
        john_edit_url = reverse("posts:edit_post",
                                kwargs={"username": StaticURLTests.user_one,
                                        "post_id": 1})

        response = self.authorized_client_john.get(john_edit_url)
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField
        }
        for form_label, expected_instance in form_fields.items():
            with self.subTest(value=form_label):
                field = response.context.get("form").fields.get(form_label)
                self.assertIsInstance(field, expected_instance)
        self.assertFalse(response.context.get("new_post"),
                         "В контекст edit_post передана new_post==False")
        self.assertEqual(response.context.get("post").text,
                         "Запись в сообществе Авиаторы")

    def test_post_created_at_index(self):
        """ Новые пост появляется на главной """
        # у нас на странице не более 10 сообщений
        self.assertEqual(len(self.contexts["posts:index"]),
                         StaticURLTests.posts_per_page,
                         "Неправильное количество постов на странице")
        self.assertEqual(self.contexts["posts:index"][1].text,
                         "11 запись")
        self.assertEqual(self.contexts["posts:index"][0].text,
                         "12 запись")

    def test_post_created_at_group(self):
        """  Пост в группу появляется только в своём сообществе """
        # Сюда должна попасть только одна запись и только нужная нам
        self.assertEqual(len(self.contexts["aviators"]), 1)

        self.assertEqual(self.contexts["aviators"][0].text,
                         "Запись в сообществе Авиаторы")

    def test_post_created_at_another_group(self):
        """  Пост в группу не появляется в другом сообществе """
        self.assertEqual(len(self.contexts["group-two"]), 0)

    def test_profile_context(self):
        test_url = reverse("posts:profile", kwargs={
                                                    "username":
                                                    StaticURLTests.user_one})
        response = self.guest_client.get(test_url)
        self.assertIsInstance(response.context.get("page"), Page)
        self.assertIn("posts_count", response.context)
        # обязательно отдаем username, на случай если нет постов
        self.assertIn("username", response.context)

        self.assertEqual(len(response.context.get("page").object_list),
                         StaticURLTests.posts_per_page,
                         "Неверное количество постов на странице")
