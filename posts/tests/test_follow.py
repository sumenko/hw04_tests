from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем 2х пользователей
        # Создаем посты от каждого
        # Подписываем первого на второго в сетапе

        cls.johndoe = get_user_model().objects.create(username="johndoe")
        cls.myst = get_user_model().objects.create(username="myst")

        Post.objects.create(text="Hello! My name is John!",
                            author=cls.johndoe,
                            group=None)

        Post.objects.create(text="My name is Myst! Hello!",
                            author=cls.myst,
                            group=None)

    def setUp(self):
        self.authorized_myst = Client()
        self.authorized_myst.force_login(FollowTests.myst)

        self.authorized_john = Client()
        self.authorized_john.force_login(FollowTests.johndoe)

    def test_follow_unfollow_test(self):
        """ Пользователи могут подписываться и отписываться друг от друга """
        pass

    # Авторизованный пользователь может подписываться на других пользователей
    #  и удалять их из подписок
    def test_follow_index(self):
        """ пользователь видит в ленте тех на кого подписался """
        # смотрим ленту до подписки john и myst
        follow_index = reverse("posts:follow_index")
        response_myst = self.authorized_myst.get(follow_index)
        response_john = self.authorized_john.get(follow_index)

        self.assertEqual(response_myst.status_code, 200,
                         "У myst без подписок не отобразилась страница")
        self.assertEqual(response_john.status_code, 200,
                         "У john без подписок не отобразилась страница")
        john_follow_myst_url = reverse("posts:profile_follow",
                                       kwargs={"username": "myst"})
        # подписывает john на myst
        response_index = self.authorized_john.get(john_follow_myst_url,
                                                  follow=True)
        self.assertEqual(response_index.status_code, 200,
                         "Не удалось получить страницу после подписки")
        # проверяем, что у myst появилось, у john нет
        response_myst = self.authorized_myst.get(follow_index)
        response_john = self.authorized_john.get(follow_index)
        self.assertEqual(response_myst.status_code, 200,
                         "Myst после подписки не смог получить страницу")
        self.assertEqual(response_john.status_code, 200,
                         "John после подписки myst не получил страницу")
        self.assertIsInstance(response_john.context.get("page")[0], Post)
        test_message = response_john.context.get("page")[0].text

        self.assertEqual(test_message, "My name is Myst! Hello!",
                         "Неверное сообщение в ленте по подписке")
        # должен появиться список с автором в контексте страницы
        self.assertEqual(response_john.context.get("authors"), [2],
                         "Передался неверный список авторов")
        # отписываем john от myst
        john_unfollow_myst_url = reverse("posts:profile_unfollow",
                                         kwargs={"username": "myst"})
        response_index = self.authorized_john.get(john_unfollow_myst_url,
                                                  follow=True)
        self.assertEqual(response_john.status_code, 200,
                         "У john без подписок не отобразилась страница")
        response_john = self.authorized_john.get(follow_index)
        # список авторов на которых подписан john должен стать пустым
        self.assertEqual(response_john.context.get("authors"), [],
                         "Передался не пустой список авторов")

    def test_unable_follow_twice(self):
        """ Проверка: подписок нет, подписка уже есть, подписка на себя """
        # подписываем myst на johndoe
        url_follow = reverse("posts:profile_follow",
                             kwargs={"username": "johndoe"})
        count_follows_before = FollowTests.johndoe.following.count()
        response = self.authorized_myst.get(url_follow, follow=True)
        self.assertEqual(response.status_code, 200,
                         "При подписке не сработал редирект")
        # сколько теперь у нашего johndoe подписчиков?
        # памятка:
        # .johndoe.follower.count()) - кого читает johndoe
        # .johndoe.following.count()) - подписчики johndoe
        count_follows_first = FollowTests.johndoe.following.count()
        self.assertEqual(count_follows_first, count_follows_before + 1,
                         "Количество подписчиков не увеличилось")
        response = self.authorized_myst.get(url_follow, follow=True)
        # количество подписчиков не должно измениться
        self.assertEqual(response.status_code, 200)
        count_follows_second = FollowTests.johndoe.following.count()
        self.assertEqual(count_follows_first, count_follows_second,
                         "Повторная подписка невозможна")
