from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .apps import BlogConfig

app_name = BlogConfig.name

router = DefaultRouter()
router.register(r"users", views.UserViewSet, basename="user")
router.register(r"posts", views.PostViewSet, basename="post")

comments_router = DefaultRouter()
comments_router.register(r"comments", views.CommentViewSet, basename="comment")

urlpatterns = [
    path("", include(router.urls)),
    path("posts/<int:post_pk>/", include(comments_router.urls)),
]
