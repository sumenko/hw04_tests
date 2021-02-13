from time import sleep

from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):  # вызывается перед запуском всех test case
        super().setUpClass()
        # наш тестовый пользователь
        cls.user_one = get_user_model().objects.create(username="Johndoe")

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
        sleep(.1)  # потому ставим задержку
        Post.objects.create(
            author=cls.user_one,
            text="Запись без сообщества",
            group=None
        )

    def setUp(self):  # вызывается перед запуском каждого test case
        # фикстуры: готовим пользователей тут
        self.guest_client = Client()

        # заходим под нашим пользователем
        self.user = get_user_model().objects.create(username="Myst")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        # соберем что выдают страницы для разных сообществ для проверки ниже
        test_urls = [
            ("index", reverse("index")),
            ("aviators", reverse("group_slug", kwargs={"slug": "aviators"})),
            ("group-two", reverse("group_slug", kwargs={"slug": "group-two"})),
        ]
        self.contexts = {}

        for group, test_url in test_urls:
            response = self.authorized_client.get(test_url)
            self.contexts[group] = response.context.get("page")

    def test_correct_template_views(self):
        """ Вызываются верные шаблоны по соответствующим им именам """
        view_templates = {
            "index.html": reverse("index"),
            "group.html": reverse("group_slug", kwargs={"slug": "aviators"}),
            "show_groups.html": reverse("show_groups"),
            "new_post.html": reverse("new_post"),
        }

        for template, reverse_name in view_templates.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_correct_context_index(self):
        """ в котнекст index передается объект Post """
        response = self.authorized_client.get(reverse("index"))
        self.assertIsInstance(response.context.get("page")[0], Post)

    def test_correct_context_group(self):
        """ в котнекст group/slug передаются объекты Post, Group """
        response = self.authorized_client.get(reverse(
            "group_slug",
            kwargs={"slug": "aviators"})
        )
        self.assertIsInstance(response.context.get("page")[0], Post)
        self.assertIsInstance(response.context.get("group"), Group)

    def test_correct_context_new_post(self):
        """ новый пост содержит текстовое поле и выбор группы """
        response = self.authorized_client.get(reverse("new_post"))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField
        }
        for form_label, expected_instance in form_fields.items():
            with self.subTest():
                field = response.context.get("form").fields.get(form_label)
                self.assertIsInstance(field, expected_instance)

    def test_post_created_at_index(self):
        """ Новые пост появляется на главной """
        # у нас в базе 2 сообщения
        self.assertEqual(len(self.contexts["index"]), 2)

        self.assertEqual(self.contexts["index"][1].text,
                         "Запись в сообществе Авиаторы")
        self.assertEqual(self.contexts["index"][0].text,
                         "Запись без сообщества")

    def test_post_created_at_group(self):
        """  Пост в группу появляется только в своём сообществе """
        # Сюда должна попасть только одна запись и только нужная нам
        self.assertEqual(len(self.contexts["aviators"]), 1)

        self.assertEqual(self.contexts["aviators"][0].text,
                         "Запись в сообществе Авиаторы")

    def test_post_created_at_another_group(self):
        """  Пост в группу не появляется в другом сообществе """
        self.assertEqual(len(self.contexts["group-two"]), 0)
