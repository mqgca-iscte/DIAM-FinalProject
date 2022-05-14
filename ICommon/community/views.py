from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
# Create your views here.

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.shortcuts import render
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from .models import Community, Post, Request, Utilizador, Reports, Comment, Likes


# Initial page
def index(request):
    communities_list = Community.objects.order_by('-creation_data')
    utilizadores_list = Utilizador.objects.order_by('-id')
    posts_list = Post.objects.order_by('-id')
    my_communities = 0
    admin_communities = 0
    # Counts number of communities the user joined
    for community in communities_list.all():
        for utilizador in community.users.all():
            if utilizador.user == request.user:
                my_communities += 1
    # Counts number of communities the user is admin
    for community in communities_list.all():
        if request.user == community.user:
            admin_communities += 1
    # If user is not admin and is authenticated sends the user in format of utilizador
    if not request.user.is_superuser and request.user.is_authenticated:
        utilizador_user = get_object_or_404(Utilizador, user_id=request.user.id)
        context = {'communities_list': communities_list, 'my_communities': my_communities,
                   'admin_communities': admin_communities, 'utilizadores_list': utilizadores_list,
                   'posts_list': posts_list, 'utilizador_user': utilizador_user}
    else:
        context = {'communities_list': communities_list, 'my_communities': my_communities,
                   'admin_communities': admin_communities, 'utilizadores_list': utilizadores_list,
                   'posts_list': posts_list}
    return render(request, 'community/index.html', context)


# Registers a new user
def registarnovo(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        userexists = authenticate(username=username, password=password)
        if userexists is not None:
            return render(request, 'community/registarnovo.html',
                          {'user': userexists, 'error_message': "User already exists", })
        else:
            myfile = request.FILES['myfile']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)
            omeuuser = User.objects.create_user(username, email, password)
            utilizador = Utilizador(user=omeuuser, image=uploaded_file_url)
            utilizador.save()
            return HttpResponseRedirect(reverse('community:index', args=""))
    else:
        return render(request, 'community/registarnovo.html',
                      {})


# Logs a user
def loginview(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if not request.user.is_superuser:
                    utilizador = get_object_or_404(Utilizador, user_id=request.user.id)
                    request.session['user_image'] = utilizador.image
                    request.session['user_id'] = request.user.id
                return HttpResponseRedirect(reverse('community:index', args=""))
            else:
                return render(request, 'community/loginview.html',
                              {'user': user,
                               'error_message': "User doesn´t exist, try with another username/password", })
        else:
            return render(request, 'community/loginview.html', {})
    else:
        return render(request, 'community/index.html',
                      {'error_message': "User is already logged, logout first before trying again"})


@login_required(login_url='/community/loginview')
# To log out the user needs to be logged
def logoutt(request):
    logout(request)
    return HttpResponseRedirect(reverse('community:index', args=""))


@login_required(login_url='/community/loginview')
def createcommunities(request):
    # The only user that can create a community is the admin
    if request.user.is_superuser:
        if request.method == 'POST':
            name = request.POST['name']
            if not name:
                return render(request, 'community/createcommunities.html',
                              {'error_message': "You weren't able to create a new community"})
            else:
                if request.method == 'POST' and request.FILES['myfile']:
                    creation_data = timezone.now()
                    myfile = request.FILES['myfile']
                    fs = FileSystemStorage()
                    filename = fs.save(myfile.name, myfile)
                    uploaded_file_url = fs.url(filename)
                    utilizador = request.user
                    c = Community.objects.create(name=name, image=uploaded_file_url,
                                                 user=utilizador, creation_data=creation_data)
                    c.save()
                return HttpResponseRedirect(reverse('community:index', args=""))
        else:
            return render(request, 'community/createcommunities.html',
                          {'error_message': "You weren´t able to create a community"})
    else:
        return render(request, 'community/index.html',
                      {'error_message': "You have no permissions to create a community"})


@login_required(login_url='/community/loginview')
def createrequest(request):
    if not request.user.is_superuser:
        if request.method == 'POST':
            name = request.POST['name']
            if not name:
                return render(request, 'community/createrequest.html',
                              {'error_message': "You weren't able to create a new request"})
            else:
                if request.method == 'POST' and request.FILES['myfile']:
                    creation_data = timezone.now()
                    myfile = request.FILES['myfile']
                    fs = FileSystemStorage()
                    filename = fs.save(myfile.name, myfile)
                    image = fs.url(filename)
                    user = request.user
                    r = Request.objects.create(name=name, image=image,
                                               user=user, creation_data=creation_data)
                    r.save()
                    return HttpResponseRedirect(reverse('community:index', args=""))
        else:
            return render(request, 'community/createrequest.html', )
    else:
        return render(request, 'community/index.html', {
            'error_message': "As an admin you have no permissions to create a request, just simply create a new community"})


@login_required(login_url='/community/loginview')
def deletecommunity(request, community_id):
    if request.user.is_superuser:
        community = get_object_or_404(Community, pk=community_id)
        community.delete()
        communities_list = Community.objects.order_by('-creation_data')[:5]
        context = {'communities_list': communities_list}
        return render(request, 'community/index.html', context)
    else:
        return render(request, 'community/index.html',
                      {'error_message': "You have no permissions to delete a community"})


@login_required(login_url='/community/loginview')
def deletepost(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    community_id = post.community.id
    community = get_object_or_404(Community, pk=community_id)
    if community.user == request.user or request.user.is_superuser:
        post.delete()
        return HttpResponseRedirect(reverse('community:viewpage', args=(community,)))
    else:
        return render(request, 'community/viewpage.html',
                      {'community': community, 'error_message': "You have no permissions to delete a community"})


@login_required(login_url='/community/loginview')
def createpost(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    user_is_in_community = False
    if not request.user.is_superuser:
        utilizador = get_object_or_404(Utilizador, user_id=request.user.id)
        if utilizador in community.users.all() or request.user == community.user:
            user_is_in_community = True
    if user_is_in_community or request.user.is_superuser:
        if request.method == 'POST':
            post = request.POST['post']
            username = request.user.username
            if request.method == 'POST' and request.FILES['myfile']:
                myfile = request.FILES['myfile']
                fs = FileSystemStorage()
                filename = fs.save(myfile.name, myfile)
                image = fs.url(filename)
                like = Likes.objects.create(user=None, likes=0)
                p = Post.objects.create(username=username, image=image, description=post, likes=like,
                                        community=community)
                p.save()
                return HttpResponseRedirect(reverse('community:viewpage', args=(community.id,)))
        else:
            return render(request, 'community/createpost.html', {'community': community})
    else:
        return render(request, 'community/viewpage.html',
                      {'community': community, 'error_message': "You don´t have permissions to create a post"})


@login_required(login_url='/community/loginview')
def likes(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    community = post.community
    user_is_in_community = False
    if not request.user.is_superuser:
        utilizador = get_object_or_404(Utilizador, user_id=request.user.id)
        if utilizador in community.users.all() or request.user == community.user:
            user_is_in_community = True
    if user_is_in_community or request.user.is_superuser:
        likes_id = post.likes.id
        filtering = Likes.objects.filter(pk=likes_id, user=request.user)
        if not filtering:
            post.likes.likes += 1
            post.likes.user = request.user
            post.likes.save()
            post.save()
            like = Likes.objects.create(user=request.user, likes=post.likes.likes)
            like.save()
            return HttpResponseRedirect(reverse('community:detailed', args=(post.id,)))
        else:
            return HttpResponseRedirect(reverse('community:detailed', args=(post.id,)))
    else:
        return render(request, 'community/viewpage.html',
                      {'community': community, 'error_message': "You don´t have permissions to like a post"})


def popular(request):
    post_popular = Post.objects.order_by('-likes__likes')[:3]
    return render(request, 'community/popularity.html', {'post_popular': post_popular})


def communityinformation(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    return render(request, 'community/communityinformation.html', {'community': community})


def detailed(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments_list = post.comments.all()
    user_admin = []
    user_community = []
    users_community = post.community.users
    if post.community.user == request.user:
        user_admin.append(post.community.user)
    if request.user.is_superuser:
        user_admin.append(request.user)
    for community_utilizador in users_community.all():
        if community_utilizador.user == request.user:
            user_community.append(community_utilizador.user)
    return render(request, 'community/detailed.html',
                  {'post': post, 'comments_list': comments_list, 'user_admin': user_admin,
                   'user_community': user_community})


@login_required(login_url='/community/loginview')
def report(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user_in_community = False
    if not request.user.is_superuser or not post.community.user == request.user:
        utilizador = get_object_or_404(Utilizador, user_id=request.user.id)
        if utilizador in post.community.users.all():
            user_in_community = True
    if user_in_community:
        if request.method == 'POST':
            reason = request.POST['reason']
            request = Reports.objects.create(post=post, reason=reason)
            request.save()
            return HttpResponseRedirect(reverse('community:detailed', args=(post.id,)))
        else:
            return render(request, 'community/report.html', {'post': post})
    else:
        return render(request, 'community/detailed.html',
                      {'post': post, 'error_message': "You don´t have permissions to report a post"})


def search(request):
    if request.method == "GET":
        searching = request.GET['search']
        communities = Community.objects.filter(name__contains=searching)
        return render(request, 'community/search.html', {'search': searching, 'communities': communities})


def searchview(request):
    return render(request, 'community/searchview.html', {})


@login_required(login_url='/community/loginview')
def seereports(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    if request.user == community.user:
        report_list = Reports.objects.order_by('-id')
        context = {'report_list': report_list, 'community': community}
        return render(request, 'community/reports.html', context)
    else:
        return render(request, 'community/index.html',
                      {'error_message': "You don´t have permissions to see the reports"})


@login_required(login_url='/community/loginview')
def ignorereport(request, reports_id):
    reports = get_object_or_404(Reports, pk=reports_id)
    community = reports.post.community
    if request.user == community.user:
        if not reports:
            return render(request, 'community/reports.html',
                          {'report': reports, 'error_message': "It was not possible to ignore the report"})
        else:
            reports.delete()
            return HttpResponseRedirect(reverse('community:index', args=""))
    else:
        return render(request, 'community/index.html',
                      {'error_message': "You have no permissions to ignore the report"})


@login_required(login_url='/community/loginview')
def deletereports(request, reports_id):
    reports = get_object_or_404(Reports, pk=reports_id)
    post_id = reports.post.id
    post = get_object_or_404(Post, pk=post_id)
    if post.community.user == request.user:
        if not post:
            return render(request, 'community/reports.html',
                          {'report': reports, 'error_message': "It was not possible to delete the report"})
        else:
            reports.delete()
            post.delete()
            return HttpResponseRedirect(reverse('community:index', args=""))
    else:
        return render(request, 'community/index.html',
                      {'error_message': "You have no permissions to delete the report"})


def viewpage(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    user_community = []
    users_community = community.users
    if community.user == request.user:
        user_community.append(community.user)
    for utilizador in users_community.all():
        if utilizador.user == request.user:
            user_community.append(utilizador.user)
    return render(request, 'community/viewpage.html', {'community': community, 'user_community': user_community})


@login_required(login_url='/community/loginview')
def createcomment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user_in_community = False
    if not request.user.is_superuser:
        utilizador = get_object_or_404(Utilizador, user_id=request.user.id)
        if utilizador in post.community.users.all() or request.user == post.community.user:
            user_in_community = True
    if user_in_community or request.user.is_superuser:
        if request.method == 'POST':
            comment = request.POST['comment']
            creation_data = timezone.now()
            user = request.user
            c = Comment.objects.create(user=user, comment=comment, creation_data=creation_data)
            c.save()
            post.comments.add(c)
            return HttpResponseRedirect(reverse('community:detailed', args=(post.id,)))
        else:
            return render(request, 'community/viewpage.html', {'community_id': post.community.id,
                                                               'error_message': "It was not possible to create a comment"})
    else:
        return render(request, 'community/index.html',
                      {'error_message': "You have no permissions to create a comment"})


@login_required(login_url='/community/loginview')
def seerequest(request):
    if request.user.is_superuser:
        request_list = Request.objects.order_by('-creation_data')
        context = {'request_list': request_list}
        return render(request, 'community/seerequest.html', context)
    else:
        return render(request, 'community/index.html',
                      {'error_message': "You have no permissions to see requests"})


@login_required(login_url='/community/loginview')
def joincommunity(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    utilizador = get_object_or_404(Utilizador, user_id=request.user.id)
    utilizador.communities.add(community)
    return HttpResponseRedirect(reverse('community:index', args=""))


@login_required(login_url='/community/loginview')
def leavecommunity(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    utilizador = get_object_or_404(Utilizador, user_id=request.user.id)
    utilizador.communities.remove(community)
    return HttpResponseRedirect(reverse('community:index', args=""))


@login_required(login_url='/community/loginview')
def mycommunities(request):
    if not request.user.is_superuser:
        user_id = request.session.get('user_id')
        utilizador = get_object_or_404(Utilizador, user_id=user_id)
        communities_list = utilizador.communities.all()
        communities_lista = Community.objects.order_by('-creation_data')
        communities_admin_list = []
        for community in communities_lista:
            if request.user == community.user:
                communities_admin_list.append(community)
        context = {'communities_list': communities_list, 'communities_admin_list': communities_admin_list}
        return render(request, 'community/mycommunity.html', context)
    else:
        return render(request, 'community/mycommunity.html',
                      {'error_message': "As an admin all communities are yours "})


@login_required(login_url='/community/loginview')
def acceptrequest(request, request_id):
    if request.user.is_superuser:
        requestt = get_object_or_404(Request, pk=request_id)
        if not requestt:
            return render(request, 'community/seerequest.html',
                          {'request': requestt, 'error_message': "Not possible to accept the request"})
        else:
            name = requestt.name
            image = requestt.image
            user = requestt.user
            creation_data = timezone.now()
            c = Community.objects.create(name=name, image=image, user=user, creation_data=creation_data)
            c.save()
            requestt.delete()
            return HttpResponseRedirect(reverse('community:index', args=""))
    else:
        return render(request, 'community/index.html',
                      {'error_message': "You have no permission to accept the request"})


@login_required(login_url='/community/loginview')
def denyrequest(request, request_id):
    if request.user.is_superuser:
        requestt = get_object_or_404(Request, pk=request_id)
        if not requestt:
            return render(request, 'community/seerequest.html',
                          {'request': requestt, 'error_message': "Not possible to deny the request"})
        else:
            requestt.delete()
            return HttpResponseRedirect(reverse('community:index', args=""))
    else:
        return render(request, 'community/index.html',
                      {'error_message': "You have no permission to deny the request"})
