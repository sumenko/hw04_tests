from django.urls import path
from django.contrib import admin

from . import views

# у нас два варианта: вывод всех постов или по сообществу
urlpatterns = [
    path("", views.index, name="index"),
    path("group/<slug:slug>/", views.group_posts, name="group_slug"),
    path("group/", views.show_groups, name="show_groups"),
    path("new/", views.new_post, name="new_post"),
    path("<str:username>/", views.profile, name="profile"),
    path("<str:username>/<int:post_id>/", views.view_post, name="post"),
    # проверить name для edit_post либо new_post
    path(
        "<str:username>/<int:post_id>/edit/",
        views.new_post,
        name="edit_post"
    ),
]
