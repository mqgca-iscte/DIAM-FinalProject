from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Utilizador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #communities = models.ManyToManyField('Community', related_name='users')


class Community(models.Model):
    name = models.CharField(max_length=100)
    image = models.TextField()
    creation_data = models.DateTimeField('data de publicacao')

    def __str__(self):
        return self.name


class Request(models.Model):
    name = models.CharField(max_length=100)
    image = models.TextField()
    user = models.ForeignKey(Utilizador, on_delete=models.CASCADE)
    creation_data = models.DateTimeField('data de publicacao')


class Post(models.Model):
    username = models.CharField(max_length=100)
    image = models.TextField()
    description = models.CharField(max_length=200)
    likes = models.IntegerField()
    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    def __str__(self):
        return self.username
