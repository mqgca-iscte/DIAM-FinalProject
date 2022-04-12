from django.urls import include, path
from . import views

app_name = 'community'
urlpatterns = [
               path("", views.index, name='index'),
               path('registarnovo', views.registarnovo, name='registarnovo'),
               path('loginview', views.loginview, name='loginview'),
               path('logoutt', views.logoutt, name='logoutt'),
               ]
