from django.contrib.auth import get_user, get_user_model
from django.contrib.auth.decorators import login_required
from django.core import paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.core.paginator import Paginator

from .forms import PostForm
from .models import Group, Post


def get_page(request, object_list):
    """ Возвращает контекст page от paginator"""
    # TODO лучше передавать реквест или извлеченный номер страницы?
    loc_paginator = Paginator(object_list, 10)
    page_number = request.GET.get("page")
    return loc_paginator.get_page(page_number)


def get_profile_data_dict(username, add_context=None):
    """ Возвращает словарь с данными профиля пользователя """
    # user = get_user_model().objects.get(username=username)
    user = get_object_or_404(get_user_model(), username=username)
    return {
            "username": username,
            "posts_count": Post.objects.filter(author=user).count(),
            "full_name": user.get_full_name()
           }


def index(request):
    """ Вывод последних 10 постов из базы """
    post_list = Post.objects.all()
    page = get_page(request, post_list)
    return render(request, "index.html", {"page": page})


def group_posts(request, slug=None):
    # Получаем объект из базы соответствующий slug
    group = get_object_or_404(Group, slug=slug)
    # Получаем все посты принадлежащие slug через related_name
    posts = group.posts.all()
    page = get_page(request, posts)
    return render(request, "group.html", {"group": group, "page": page})


def show_groups(request):
    """ Показывает страницу со списком всех сообществ """
    groups = Group.objects.all()[:10]
    return render(request, "show_groups.html", {"groups": groups})


def profile(request, username):
    """ Выводит профиль пользователя и его посты """
    # цепляем данные профиля
    context = get_profile_data_dict(username)
    user = get_user_model().objects.get(username=username)
    posts = user.posts.all()
    page = get_page(request, posts)
    context.update({"page": page})
    # обязательно отдаем username и full_name, на случай если нет постов
    return render(request, "profile.html", context)


def view_post(request, username, post_id):
    """ Посмотреть пост под номером post_id """
    context = {"post": Post.objects.get(id=post_id), "post_id": post_id}
    context.update(get_profile_data_dict(username))
    return render(request, "post.html", context)


@login_required
def new_post(request, username=None, post_id=None):
    """ Создать/редактировать новый пост """
    instance = None
    if username and post_id:  # Если установлены - значит редактирование
        user = get_object_or_404(get_user_model(), username=username)
        instance = get_object_or_404(Post, author=user, id=post_id)

    form = PostForm(request.POST or None, instance=instance)

    if request.GET or not form.is_valid():
        return render(request, "new_post.html", {"form": form})

    post = form.save(commit=False)
    post.author = request.user
    post.save()

    return redirect(reverse_lazy("index"))
