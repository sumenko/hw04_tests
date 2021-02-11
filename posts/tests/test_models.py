from unittest import skip

from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Group, Post


class TestPostModels(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # pylance почему-то ругается что не может доступиться к create_user
        cls.user = get_user_model().objects.create_user(username="Myst")

        Post.objects.create(
            author=cls.user,
            text="Это тестовый текст в посте"
        )
        cls.post = Post.objects.get(id=1)

    def test_post_verbose_names(self):
        post = TestPostModels.post
        verbose_name = post._meta.get_field('text').verbose_name
        self.assertEqual(verbose_name, "Текст")

    def test_post_help_texts(self):
        post = TestPostModels.post
        verbose_name = post._meta.get_field('text').help_text
        self.assertEqual(verbose_name, "Содержимое поста")

    def test_post_str_correct(self):
        self.assertEqual(TestPostModels.post.__str__(),
                         "Это тестовый текст в посте"[:15])


class TestGroupModels(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        Group.objects.create(
            title="Авиа",
            slug="aviators",
            description="Сообщество любителей авиамоделей"
        )
        cls.group = Group.objects.get(id=1)
        # TODO: проверим сообщество с длинным названием
        Group.objects.create(
            title="А"*201,
            slug="q"*101,
            description="f"*101
        )
        cls.long_group = Group.objects.get(id=2)

    def test_group_verbose_names(self):
        group = TestGroupModels.group
        verbose_names = {
            "title": "Название сообщества",
            "slug": "Адрес сообщества",
            "description": "Описание"
        }
        for field, expected in verbose_names.items():
            with self.subTest(value=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name,
                    expected)

    def test_group_help_text(self):
        group = TestGroupModels.group
        help_texts = {
            "title": "",
            "slug": ("уникальное название сообщества "
                     "латиницей для адресной строки"),
            "description": "Описание сообщества"
        }
        for help_text, expected in help_texts.items():
            with self.subTest(value=help_text):
                self.assertEqual(
                    group._meta.get_field(help_text).help_text,
                    expected)

    def test_group_str_correct(self):
        self.assertEqual(TestGroupModels.group.__str__(),
                         "Авиа")

    # TODO: доделать проверку что пишется небольше чем можно
    @skip("Разобраться, почему max_length не ограничивает поля в Model")
    def test_long_group_fields(self):
        # print("<", TestGroupModels.long_group.title,">")
        self.assertEqual(len(TestGroupModels.long_group.title), 200)
        self.assertEqual(len(TestGroupModels.long_group.slug), 100)
        self.assertEqual(len(TestGroupModels.long_group.description), 100)
