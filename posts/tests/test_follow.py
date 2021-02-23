from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post


class StaticURLTests(TestCase):
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
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(StaticURLTests.myst)
    
    def test_follow_unfollow_test(self):
        """ Пользователи могут подписываться и отписываться друг от друга """
        pass

    def test_follow_index(self):
        """ пользователь видит в ленте тех на кого подписался """
        # смотрим ленту до подписки
        john_follow_index = reverse("posts:follow_index")
        response = self.authorized_client.get(john_follow_index)
        print(response.context.get["page"])
        self.assertEqual(response.status_code, 200,
                         "У пользователя без подписок не отобразилась страница"
                        )
        response = self.authorized_client.get(john_follow_myst_url)
        john_follow_myst_url = reverse("posts:follow",
                                       kwargs={"username": "myst"})
        response = self.authorized_client.get(john_follow_myst_url)

    def test_user_not_followed_index(self):
        """ пользователь невидит в ленте тех на кого не подписался """
        pass

    # Авторизованный пользователь может подписываться на других пользователей
    #  и удалять их из подписок
    def test_unable_follow_twice(self):
        """ Проверка: подписок нет, подписка уже есть, подписка на себя """
        # подписываем myst на johndoe
        url_follow = reverse("posts:profile_follow",
                             kwargs={"username": "johndoe"})
        count_follows_before = StaticURLTests.johndoe.following.count()
        response = self.authorized_client.get(url_follow, follow=True)
        self.assertEqual(response.status_code, 200,
                         "При подписке не сработал редирект")
        # сколько теперь у нашего johndoe подписчиков?
        # памятка:
        # StaticURLTests.johndoe.follower.count()) - кого читает johndoe
        # StaticURLTests.johndoe.following.count()) - подписчики johndoe
        count_follows_first = StaticURLTests.johndoe.following.count()
        self.assertEqual(count_follows_first, count_follows_before + 1,
                         "Количество подписчиков не увеличилось")
        response = self.authorized_client.get(url_follow, follow=True)
        # количество подписчиков не должно измениться
        self.assertEqual(response.status_code, 200)
        count_follows_second = StaticURLTests.johndoe.following.count()
        self.assertEqual(count_follows_first, count_follows_second,
                         "Повторная подписка невозможна")

