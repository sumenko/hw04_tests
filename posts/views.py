import datetime as dt

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from .forms import PostForm
from .models import Group, Post


def get_page(request, object_list):
    """ Возвращает контекст page от paginator"""
    # TODO лучше передавать реквест или извлеченный номер страницы?
    loc_paginator = Paginator(object_list, 10)
    page_number = request.GET.get("page")
    return loc_paginator.get_page(page_number), loc_paginator


def get_profile_data_dict(username, add_context=None):
    """ Возвращает словарь с данными профиля пользователя """
    # user = get_user_model().objects.get(username=username)
    user = get_object_or_404(get_user_model(), username=username)
    return {
            "username": user,
            "posts_count": Post.objects.filter(author=user).count(),
           }


def index(request):
    """ Вывод последних 10 постов из базы """
    post_list = Post.objects.all()
    page, paginator = get_page(request, post_list)
    return render(request,
                  "index.html",
                  {"page": page,
                   "paginator": paginator})


def group_posts(request, slug=None):
    # Получаем объект из базы соответствующий slug
    group = get_object_or_404(Group, slug=slug)
    # Получаем все посты принадлежащие slug через related_name
    posts = group.posts.all()
    page, paginator = get_page(request, posts)
    return render(request,
                  "group.html",
                  {"group": group,
                   "page": page,
                   # передаем paginator в контекст чтобы пройти тест
                   "paginator": paginator})


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
    page, paginator = get_page(request, posts)  # костыль paginator для тестов
    context.update({"page": page, "paginator": paginator})

    # обязательно отдаем username и full_name, на случай если нет постов
    return render(request, "profile.html", context)


def view_post(request, username, post_id):
    """ Посмотреть пост под номером post_id """
    user = get_object_or_404(get_user_model(), username=username)
    post = get_object_or_404(Post, id=post_id, author=user)
    context = {"post": post, "post_id": post_id}
    context.update(get_profile_data_dict(username))
    return render(request, "post.html", context)


@login_required
def new_post(request, username=None, post_id=None):
    """ Создать/редактировать новый пост """
    # !!! TODO сделать названия кнопок другие и страницы для едит и нью
    instance = None
    new_post = True  # поумолчанию - создать если ниже не сказано иное
    # не тот пользователь - уходим
    if request.user.username != username and post_id:
        return redirect("post", username, post_id)

    if username and post_id:  # Если установлены - значит редактирование
        user = get_object_or_404(get_user_model(), username=username)
        instance = get_object_or_404(Post, author=user, id=post_id)
        new_post = False

    form = PostForm(request.POST or None, instance=instance)

    if request.GET or not form.is_valid():
        return render(request, "new_post.html",
                      {"form": form,
                       "new_post": new_post,
                       "post": instance})  # тест просит, но для чего не ясно

    post = form.save(commit=False)
    post.pub_date = dt.datetime.now()
    post.author = request.user
    post.save()
    # если доши сюда и пользователь совпадает, значит вернемся к посту
    if request.user.username == username:
        return redirect("post", username, post_id)

    return redirect(reverse_lazy("index"))
