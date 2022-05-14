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
               path('<int:community_id>/leave', views.leavecommunity, name='leavecommunity'),
               path('<int:community_id>/delete', views.deletecommunity, name='deletecommunity'),
               path('mycommunities', views.mycommunities, name='mycommunities'),
               path('view/<int:community_id>', views.viewpage, name='viewpage'),
               path('view/<int:community_id>/createpost', views.createpost, name='createpost'),
               path('detailed/<int:post_id>/likes', views.likes, name='likes'),
               path('detailed/<int:post_id>', views.detailed, name='detailed'),
               path('detailed/<int:post_id>/deletepost', views.deletepost, name='deletepost'),
               path('detailed/<int:post_id>/report', views.report, name='report'),
               path('seereports/<int:community_id>', views.seereports, name="seereports"),
               path('popularity', views.popular, name="popularity"),
               path('searchview', views.searchview, name="searchview"),
               path('searchview/search', views.search, name="search"),
               path('seereports/<int:reports_id>/ignorereport', views.ignorereport, name='ignorereport'),
               path('seereports/<int:reports_id>/deletereports', views.deletereports, name='deletereports'),
               path('detailed/<int:post_id>/createcomment', views.createcomment, name='createcomment'),
               path('view/<int:community_id>/communityinformation', views.communityinformation, name='communityinformation'),
               ]
