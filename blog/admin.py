from datetime import timedelta, date

from django.contrib import admin
from django.utils.html import format_html
from .models import User, Post, Comment
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.admin import DateFieldListFilter


class CustomDateFilter(DateFieldListFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Добавляем дополнительные варианты фильтрации
        self.links = list(self.links)
        self.links.insert(
            2,
            (
                "Последние 7 дней",
                {
                    self.lookup_kwarg_since: str(date.today() - timedelta(days=7)),
                    self.lookup_kwarg_until: str(date.today()),
                },
            ),
        )
        self.links.insert(
            3,
            (
                "Последние 30 дней",
                {
                    self.lookup_kwarg_since: str(date.today() - timedelta(days=30)),
                    self.lookup_kwarg_until: str(date.today()),
                },
            ),
        )


class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "display_author_link", "created_at", "updated_at")
    list_filter = ("created_at", "author", CustomDateFilter)
    search_fields = ("title", "text", "author__username")
    date_hierarchy = "created_at"  # Иерархия по дате создания
    readonly_fields = ("created_at", "updated_at")

    # Метод для отображения ссылки на автора
    def display_author_link(self, obj):
        return format_html(
            '<a href="/admin/blog/user/{}/">{}</a>', obj.author.id, obj.author.username
        )

    display_author_link.short_description = "Автор"
    display_author_link.admin_order_field = "author__username"

    def delete_old_posts(self, request, queryset):
        """Удаление постов старше 1 года"""
        from datetime import datetime, timedelta

        one_year_ago = datetime.now() - timedelta(days=365)
        old_posts = queryset.filter(created_at__lt=one_year_ago)
        count = old_posts.count()
        old_posts.delete()
        self.message_user(request, f"Удалено {count} старых постов.")

    delete_old_posts.short_description = "Удалить посты старше 1 года"

    def mark_as_featured(self, request, queryset):
        """Пометить посты как избранные (добавляем пример кастомного поля)"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"Помечено {updated} постов как избранные.")

    mark_as_featured.short_description = "Пометить как избранные"

    actions = ["delete_old_posts", "mark_as_featured"]


class CommentAdmin(admin.ModelAdmin):
    list_display = ("short_text", "author", "post", "created_at")
    list_filter = ("created_at", "author")
    search_fields = ("text", "author__username", "post__title")

    def short_text(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text

    short_text.short_description = "Текст комментария"


# Кастомизация админки для пользователя
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "phone", "birth_date", "is_staff")
    list_filter = ("is_staff", "is_superuser", "created_at")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Персональная информация", {"fields": ("email", "phone", "birth_date")}),
        (
            "Права",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Важные даты", {"fields": ("last_login", "created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at")
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "phone",
                    "birth_date",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


# Регистрация моделей
admin.site.register(User, UserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
