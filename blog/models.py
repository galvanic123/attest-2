from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from .validators import (
    validate_password_complexity,
    validate_email_domain,
    validate_adult,
    validate_title_no_bad_words
)


class User(AbstractUser):
    phone = models.CharField(max_length=20, verbose_name='Номер телефона')
    birth_date = models.DateField(
        verbose_name='Дата рождения',
        null=True,
        blank=True,
        validators=[validate_adult]  # Добавляем валидатор возраста
    )
    email = models.EmailField('email address',
        unique=True,
        validators=[validate_email_domain]  # Добавляем валидатор email
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата редактирования')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # Валидация пароля при создании пользователя
        if not self.pk and self.password:
            validate_password_complexity(self.password)
        super().save(*args, **kwargs)


class Post(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name='Заголовок',
        validators=[validate_title_no_bad_words]  # Валидатор запрещенных слов
    )
    text = models.TextField(verbose_name='Текст')
    image = models.ImageField(
        upload_to='posts/',
        verbose_name='Изображение',
        null=True,
        blank=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата редактирования')

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        # Дополнительная валидация возраста автора при сохранении поста
        if self.author and self.author.birth_date:
            validate_adult(self.author.birth_date)


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    text = models.TextField(verbose_name='Текст')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата редактирования')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']

    def __str__(self):
        return f'Комментарий от {self.author} к посту "{self.post.title}"'
