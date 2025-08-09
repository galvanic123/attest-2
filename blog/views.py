from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import User, Post, Comment
from .serializers import UserCreateSerializer, UserSerializer, PostSerializer, CommentSerializer
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from .validators import validate_adult


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    def update(self, request, *args, **kwargs):
        if not request.user.is_staff and request.user.id != int(kwargs['pk']):
            return Response(
                {"detail": "Вы можете редактировать только свой профиль."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {"detail": "Только администратор может удалять пользователей."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        try:
            # Проверка возраста перед созданием поста
            if self.request.user.birth_date:
                validate_adult(self.request.user.birth_date)
            serializer.save(author=self.request.user)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

    def update(self, request, *args, **kwargs):
        post = self.get_object()
        if not request.user.is_staff and post.author != request.user:
            return Response(
                {"detail": "Вы можете редактировать только свои посты."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        if not request.user.is_staff and post.author != request.user:
            return Response(
                {"detail": "Вы можете удалять только свои посты."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        post_pk = self.kwargs.get('post_pk')
        return Comment.objects.filter(post_id=post_pk)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_pk'))
        serializer.save(author=self.request.user, post=post)

    def update(self, request, *args, **kwargs):
        comment = self.get_object()
        if not request.user.is_staff and comment.author != request.user:
            return Response(
                {"detail": "Вы можете редактировать только свои комментарии."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        if not request.user.is_staff and comment.author != request.user:
            return Response(
                {"detail": "Вы можете удалять только свои комментарии."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
