from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Utilizador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.TextField()


class Community(models.Model):
    name = models.CharField(max_length=100)
    image = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_data = models.DateTimeField('data de publicacao')
    users = models.ManyToManyField('Utilizador', related_name='communities')

    def __str__(self):
        return self.name


class Request(models.Model):
    name = models.CharField(max_length=100)
    image = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_data = models.DateTimeField('data de publicacao')


class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    likes = models.IntegerField()


class Post(models.Model):
    username = models.CharField(max_length=100)
    image = models.TextField()
    description = models.CharField(max_length=200)
    likes = models.ForeignKey(Likes, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    comments = models.ManyToManyField('Comment', related_name='posts')

    def __str__(self):
        return self.username


class Reports(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    reason = models.CharField(max_length=200)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=200)
    creation_data = models.DateTimeField('data de publicacao')