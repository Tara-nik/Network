from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    posts = models.ForeignKey('Post', on_delete=models.CASCADE, default=None, blank=True, null=True)
    followers = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='user_followers')
    following = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='user_following')

    def serialize(self):
        return {
            "id": self.id,
            "posts": self.posts.serialize() if self.posts else None,
            "username": self.username,
            "email": self.email,
            "following": [user.username for user in self.following.all()],
            "followers": [user.username for user in self.followers.all()]
        }


class Post(models.Model):
    writer = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True, blank=True)
    content = models.CharField(max_length=250)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='user_likes', blank=True)

    def serialize(self):
        return {
            "id": self.id,
            "user": self.writer.username if self.witer else None,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "likes_count": self.likes.count()
        }
