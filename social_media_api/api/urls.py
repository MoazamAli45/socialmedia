# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter(trailing_slash=False)
router.register(r'posts', views.PostViewSet)
router.register(r'comments', views.CommentViewSet)
router.register(r'follows', views.FollowViewSet)
router.register(r'users', views.UserViewSet, basename='user')


urlpatterns = [
    path('', views.home, name='home'),
    path('', include(router.urls)),
    path('signup', views.signup, name='signup'),
    path('login', views.login, name='login'),
    path('password_reset', views.password_reset, name='password_reset'),
    path('password_reset_confirm', views.password_reset_confirm, name='password_reset_confirm'),
]