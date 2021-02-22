from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import (get_list_or_404, get_object_or_404, redirect,
                              render)
from django.urls import reverse_lazy
from django.utils import timezone

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post


def follow_authors_context(request):
    """ передает список подписки на авторов для оформления кнопок """
    if not request.user.is_authenticated:
        return None
    links = Follow.objects.filter(user=request.user)
    authors = [link.author.id for link in links]
    return authors


@login_required
def view_follow_index(request):
    """ Вывод ленты подписок пользователя """
    # собираем все подписки пользователя
    authors = follow_authors_context(request)
    posts = Post.objects.prefetch_related("author").filter(author__in=authors)

    page, paginator = get_page(request, posts)
    context = {"page": page, "paginator": paginator, "follow_index": True,
               "username": request.user, "authors": authors}

    return render(request, "index.html", context)


@login_required
def profile_follow(request, username):
    """ подписывает текущего пользователя на автора """
    if username == request.user.username:
        # TODO заменить
        return redirect("posts:index")
    user = get_object_or_404(get_user_model(), username=request.user)
    author = get_object_or_404(get_user_model(), username=username)
    count = Follow.objects.filter(user=user, author=author).count()

    if not count:
        Follow.objects.create(user=user, author=author)
    # TODO: проверить, что редирект с нашего сайта
    redirect_link = request.GET.get("next")
    # вернем пользователя туда откуда пришёл
    if redirect_link:
        return redirect(redirect_link)
    else:
        return redirect("/")


@login_required
def profile_unfollow(request, username):
    """ отписывает текущего пользователя на автора """
    user = get_object_or_404(get_user_model(), username=request.user)
    author = get_object_or_404(get_user_model(), username=username)

    count = Follow.objects.filter(user=user, author=author).count()

    if count:
        Follow.objects.get(user=user, author=author).delete()

    redirect_link = request.GET.get("next")
    if redirect_link:
        return redirect(redirect_link)
    else:
        return redirect("/")


def get_page(request, object_list):
    """ Возвращает контекст page от paginator """
    loc_paginator = Paginator(object_list, 10)
    page_number = request.GET.get("page")
    return loc_paginator.get_page(page_number), loc_paginator


def get_profile_data_dict(username, add_context=None):
    """ Возвращает словарь с данными профиля и объектом пользователя """
    user = get_object_or_404(get_user_model(), username=username)
    context = {
        "username": user,
        "posts_count": Post.objects.filter(author=user).count(),
               }
    if add_context:
        context.update(add_context)
    return context


def index(request):
    """ Вывод последних 10 постов из базы """
    # post_list = Post.objects.all()
    post_list = Post.objects.prefetch_related("author").all()
    page, paginator = get_page(request, post_list)
    context = {"page": page, "paginator": paginator}

    authors = follow_authors_context(request)
    context.update({"authors": authors})
    return render(request, "index.html", context)


def group_posts(request, slug=None):
    # Получаем объект из базы соответствующий slug
    group = get_object_or_404(Group, slug=slug)
    # Получаем все посты принадлежащие slug через related_name
    posts = group.posts.prefetch_related("author").all()
    page, paginator = get_page(request, posts)
    # передаем paginator в контекст чтобы пройти тест
    context = {"group": group, "page": page, "paginator": paginator,
               "authors": follow_authors_context(request)}

    return render(request, "group.html", context)


def show_groups(request):
    """ Показывает страницу со списком всех сообществ """
    groups = get_list_or_404(Group)
    return render(request, "show_groups.html", {"groups": groups})


def profile(request, username):
    """ Выводит профиль пользователя и его посты """
    # цепляем данные профиля
    context = get_profile_data_dict(username)
    posts = context["username"].posts.prefetch_related("author").all()
    page, paginator = get_page(request, posts)  # костыль paginator для тестов
    author = get_object_or_404(get_user_model(), username=username)
    # подписан ли текущий пользователь на того что в профиле
    follow = False
    if (request.user.is_authenticated and
       Follow.objects.filter(user=request.user, author=author).exists()):
        follow = True
    # count = Follow.objects.filter(user=request.user, author=author).count()
    # follow = True if count else False
    context.update({"page": page, "paginator": paginator, "following": follow})

    # обязательно отдаем username, на случай если нет постов
    return render(request, "profile.html", context)


def view_post(request, username, post_id):
    """ Посмотреть пост под номером post_id """
    context = get_profile_data_dict(username)
    post = get_object_or_404(Post, id=post_id,
                             author__username=context["username"])
    comments = Comment.objects.filter(post=post_id)
    # Так не работает, потому что может не быть комментариев, тогда придет 404
    # comments = get_list_or_404(Comment, post=post_id)
    form = CommentForm()
    context.update({"post": post, "post_id": post_id,
                    "comments": comments, "form": form})
    return render(request, "post.html", context)


@login_required
def add_comment(request, username, post_id):
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = get_object_or_404(get_user_model(),
                                           username=request.user)
        comment.post = get_object_or_404(Post, id=post_id)
        comment.save()
    return redirect("posts:post", username, post_id)


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
