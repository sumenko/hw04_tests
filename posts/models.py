from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    """ описание поста """
    text = models.TextField(verbose_name="Текст",
                            help_text="Содержимое поста")

    pub_date = models.DateTimeField(verbose_name="Дата публикации",
                                    auto_now_add=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="posts",
                               verbose_name="Автор")
    # создаем связь поста с сообществом
    group = models.ForeignKey("Group", on_delete=models.SET_NULL,
                              blank=True,
                              null=True,
                              related_name="posts",
                              verbose_name="Сообщество",
                              help_text="Название сообщества")

    image = models.ImageField(upload_to="posts/", blank=True, null=True)

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    """ описание сообщества """
    title = models.CharField("Название сообщества", max_length=200)
    slug = models.SlugField("Адрес сообщества", max_length=100, unique=True,
                            help_text=("уникальное название сообщества "
                                       "латиницей для адресной строки"))

    description = models.TextField("Описание", max_length=100,
                                   default="",
                                   help_text="Описание сообщества")

    def __str__(self):
        """ Выводим поле title"""
        return self.title
