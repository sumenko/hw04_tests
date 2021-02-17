from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone

from .forms import PostForm
from .models import Group, Post


def get_page(request, object_list):
    """ Возвращает контекст page от paginator """
    loc_paginator = Paginator(object_list, 10)
    page_number = request.GET.get("page")
    return loc_paginator.get_page(page_number), loc_paginator


def get_profile_data_dict(username, add_context=None):
    """ Возвращает словарь с данными профиля и объектом пользователя """
    user = get_object_or_404(get_user_model(), username=username)
    return {
        "username": user,
        "posts_count": Post.objects.filter(author=user).count()
    }


def index(request):
    """ Вывод последних 10 постов из базы """
    post_list = Post.objects.all()
    page, paginator = get_page(request, post_list)
    context = {"page": page, "paginator": paginator}
    return render(request, "index.html", context)


def group_posts(request, slug=None):
    # Получаем объект из базы соответствующий slug
    group = get_object_or_404(Group, slug=slug)
    # Получаем все посты принадлежащие slug через related_name
    posts = group.posts.all()
    page, paginator = get_page(request, posts)
    return render(request,
                  "group.html",
                  {"group": group, "page": page,
                   # передаем paginator в контекст чтобы пройти тест
                   "paginator": paginator}
                  )


def show_groups(request):
    """ Показывает страницу со списком всех сообществ """
    groups = Group.objects.all()[:10]
    return render(request, "show_groups.html", {"groups": groups})


def profile(request, username):
    """ Выводит профиль пользователя и его посты """
    # цепляем данные профиля
    context = get_profile_data_dict(username)
    posts = context["username"].posts.all()
    page, paginator = get_page(request, posts)  # костыль paginator для тестов
    context.update({"page": page, "paginator": paginator})

    # обязательно отдаем username, на случай если нет постов
    return render(request, "profile.html", context)


def view_post(request, username, post_id):
    """ Посмотреть пост под номером post_id """
    context = get_profile_data_dict(username)
    post = get_object_or_404(Post, id=post_id,
                             author__username=context["username"])
    context.update({"post": post, "post_id": post_id})
    return render(request, "post.html", context)


@login_required
def new_post(request, username=None, post_id=None):
    """ Создать/редактировать новый пост """
    instance = None
    new_post = True  # поумолчанию - создать если ниже не сказано иное
    # не тот пользователь - уходим
    if request.user.username != username and post_id:
        return redirect("posts:post", username, post_id)

    if username and post_id:  # Если установлены - значит редактирование
        instance = get_object_or_404(Post,
                                     author__username=username,
                                     id=post_id)
        new_post = False

    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=instance)

    if request.GET or not form.is_valid():
        return render(request, "new_post.html",
                      {"form": form,
                       "new_post": new_post,
                       "post": instance})  # тест просит, но для чего не ясно

    post = form.save(commit=False)
    post.pub_date = timezone.now()
    post.author = request.user
    post.save()
    # если дошли сюда и пользователь совпадает, значит вернемся к посту
    if request.user.username == username:
        return redirect("posts:post", username, post_id)

    return redirect(reverse_lazy("posts:index"))


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)
