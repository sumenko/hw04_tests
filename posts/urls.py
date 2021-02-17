from django.urls import path

from . import views

app_name = "posts"

# у нас два варианта: вывод всех постов или по сообществу
urlpatterns = [
    path("404/", views.page_not_found, name="404"),
    path("500/", views.server_error, name="500"),
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
