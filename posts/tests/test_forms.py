from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post


class TestForms(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create(username="johndoe")
        Post.objects.create(
            author=cls.user,
            text="Этот текст должен быть изменен",
            group=None
        )

    def setUp(self):
        self.authorized_client = Client()
        self.user = get_user_model().objects.get(username="johndoe")
        self.authorized_client.force_login(self.user)

    def test_new_post_added(self):
        """ Проверяем что при добавлении записей стало больше на 1 """

        posts_count = Post.objects.count()

        form_data = {
            "text": "test message",
            "author": self.user,
            "group": ""
        }
        self.authorized_client.post(
            reverse("posts:new_post"),
            data=form_data,
            follow=True
        )
        # проверяем что постов прибавилось
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_empty_record_not_added(self):
        """ проверим что пустая запись не добавляется """

        posts_count = Post.objects.count()

        form_data = {
            "text": "",
            "author": self.user,
            "group": ""
        }
        self.authorized_client.post(
            reverse("posts:new_post"),
            data=form_data,
            follow=True
        )
        # проверяем что постов не прибавилось
        self.assertEqual(Post.objects.count(), posts_count)

    def test_edited_post_changed(self):
        """ Текст в базе должен измениться после редактирования поста """
        form_data = {
            "text": "Измененный текст",
            "author": self.user,
            "group": ""
        }
        self.authorized_client.post(
            reverse("posts:edit_post",
                    kwargs={"username": self.user.username, "post_id": 1}),
            data=form_data,
            follow=True
        )
        edited_post = get_object_or_404(Post, id=1)
        self.assertEqual(edited_post.text, "Измененный текст",
                         "Текст в базе не имезменился после редактирования")
