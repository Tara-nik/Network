from django.urls import path

from . import views




urlpatterns = [
    path("", views.index, name="index"),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.register, name='register'),

    path('new_post', views.new_post, name='new_post'),
    path('all-posts', views.all_posts, name='all_posts'),
    path('following/', views.following_posts, name='following_posts'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('like_post/<int:post_id>/', views.like_post, name='like_post'),
    path('edit_post/<int:post_id>/', views.edit_post, name='edit_post'),
    path('follow/<str:username>/', views.follow, name='follow'),
    path('unfollow/<str:username>/', views.unfollow, name='unfollow'),
]