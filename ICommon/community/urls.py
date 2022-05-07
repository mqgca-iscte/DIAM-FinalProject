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
               path('<int:community_id>/join', views.joincommunity, name='joincommunity'),
               path('mycommunities', views.mycommunities, name='mycommunities'),
               path('view/<int:community_id>', views.viewpage, name='viewpage'),
               path('view/<int:community_id>/createpost', views.createpost, name='createpost'),
               path('detailed/<int:post_id>', views.detailed, name='detailed'),
               path('detailed/<int:post_id>/likes', views.likes, name='likes'),
               path('detailed/<int:post_id>/report', views.report, name='report'),
               path('seereports', views.seereports, name="seereports"),
               path('seereports/<int:reports_id>/ignorereport', views.ignorereport, name='ignorereport'),
               path('seereports/<int:reports_id>/deletereports', views.deletereports, name='deletereports'),
               path('detailed/<int:post_id>/createcomment', views.createcomment, name='createcomment'),
               ]
