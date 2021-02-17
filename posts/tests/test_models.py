from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post


class TestPostModels(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(username="Myst")

        cls.post = Post.objects.create(
            author=cls.user,
            text="Это тестовый текст в посте")

    def test_post_verbose_names(self):
        post = TestPostModels.post
        verbose_names = [
            ('text', 'Текст'),
            ('image', 'Картинка'),
        ]
        for field_name, verbose_name in verbose_names:
            with self.subTest(value=field_name):
                test_name = post._meta.get_field(field_name).verbose_name
                self.assertEqual(test_name, verbose_name)

    def test_post_help_texts(self):
        post = TestPostModels.post
        help_texts = [
            ('text', 'Содержимое поста'),
            ('image', 'Картинка к посту'),
        ]
        for field_name, help_text in help_texts:
            with self.subTest(value=field_name):
                test_name = post._meta.get_field(field_name).help_text
                self.assertEqual(test_name, help_text)
        # help_text = post._meta.get_field(field_name).help_text
        # self.assertEqual(text_name, help_text)

    def test_post_str_correct(self):
        self.assertEqual(TestPostModels.post.__str__(),
                         "Это тестовый текст в посте"[:15])


class TestGroupModels(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title="Авиа",
            slug="aviators",
            description="Сообщество любителей авиамоделей"
        )
        # TODO: проверим сообщество с длинным названием
        Group.objects.create(
            title="А" * 200,
            slug="q" * 100,
            description="f" * 100
        )
        cls.long_group = Group.objects.get(id=2)

    def test_group_verbose_names(self):
        group = TestGroupModels.group
        verbose_names = {
            "title": "Название сообщества",
            "slug": "Адрес сообщества",
            "description": "Описание",
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
            "description": "Описание сообщества",
        }
        for help_text, expected in help_texts.items():
            with self.subTest(value=help_text):
                self.assertEqual(
                    group._meta.get_field(help_text).help_text,
                    expected)

    def test_group_str_correct(self):
        self.assertEqual(TestGroupModels.group.__str__(),
                         "Авиа")
