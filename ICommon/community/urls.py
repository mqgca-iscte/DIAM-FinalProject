from django.urls import include, path
from . import views

app_name = 'community'
urlpatterns = [
               path("", views.index, name='index'),
               path('registarnovo', views.registarnovo, name='registarnovo'),
               path('loginview', views.loginview, name='loginview'),
               path('logoutt', views.logoutt, name='logoutt'),
               path('criar', views.createcommunities, name='createcommunities'),
               path('createrequest', views.createrequest, name='createrequest'),
               path('seerequest', views.seerequest, name='seerequest'),
               path('<int:request_id>/acceptrequest', views.acceptrequest, name='acceptrequest'),
               path('<int:request_id>/denyrequest', views.denyrequest, name='denyrequest'),
               ]
