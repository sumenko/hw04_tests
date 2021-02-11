from django.contrib import admin
from .models import Post, Group


class PostAdmin(admin.ModelAdmin):
    # Перечисляем поля для отображения в таблице
    list_display = ("pk", "text", "pub_date", "author", "group")
    # Перечисляем поля по которым можно будет искать
    search_fields = ("text", "group")
    # фильтр
    list_filter = ("pub_date",)
    # если пустое значение то...
    empty_value_display = "-пусто-"


class GroupAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "slug", "description")
    search_fields = ("title", "description")
    empty_value = "-пусто-"


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
