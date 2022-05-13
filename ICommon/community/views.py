from django.contrib.auth import authenticate, login, logout
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

from .models import Community, Post, Request, Utilizador, Reports, Comment, Likes


def index(request):
    communities_list = Community.objects.order_by('-creation_data')
    utilizadores_list = Utilizador.objects.order_by('-id')
    posts_list = Post.objects.order_by('-id')
    my_communities = 0
    admin_communities = 0
    for community in communities_list.all():
        for utilizador in community.users.all():
            if utilizador.user == request.user:
                my_communities += 1
    for community in communities_list.all():
        if request.user == community.user:
            admin_communities += 1
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


def registarnovo(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        userexists = authenticate(username=username, password=password)
        if userexists is not None:
            return render(request, 'community/registarnovo.html',
                          {'user': userexists, 'error_message': "User já existente", })
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
        return render(request, 'community/registarnovo.html', {})


def loginview(request):
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
                           'error_message': "User não existe, tente de novo com outro username/password", })
    else:
        return render(request, 'community/loginview.html', {})


def logoutt(request):
    logout(request)
    communities_list = Community.objects.order_by('-creation_data')
    context = {'communities_list': communities_list}
    return render(request, 'community/index.html', context)


def createcommunities(request):
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
                if request.user.is_superuser:
                    utilizador = request.user
                    c = Community.objects.create(name=name, image=uploaded_file_url,
                                                 user=utilizador, creation_data=creation_data)
                    c.save()
                else:
                    user_id = request.session.get('user_id')
                    utilizador = get_object_or_404(Utilizador, user_id=user_id)
                    c = Community.objects.create(name=name, image=uploaded_file_url, user=utilizador,
                                                 creation_data=creation_data)
                    c.save()
            return HttpResponseRedirect(reverse('community:index', args=""))
    else:
        return render(request, 'community/createcommunities.html', {})


def createrequest(request):
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
        return render(request, 'community/createrequest.html', {})


def deletecommunity(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    community.delete()
    communities_list = Community.objects.order_by('-creation_data')[:5]
    context = {'communities_list': communities_list}
    return render(request, 'community/index.html', context)


def deletepost(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post.delete()
    community_id = post.community.id
    community = get_object_or_404(Community, pk=community_id)
    return HttpResponseRedirect(reverse('community:viewpage', args=(community.id,)))


def createpost(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    if request.method == 'POST':
        post = request.POST['post']
        username = request.user.username
        if request.method == 'POST' and request.FILES['myfile']:
            myfile = request.FILES['myfile']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            image = fs.url(filename)
            like = Likes.objects.create(user=None, likes=0)
            p = Post.objects.create(username=username, image=image, description=post, likes=like, community=community)
            p.save()
            return HttpResponseRedirect(reverse('community:viewpage', args=(community.id,)))
    else:
        return render(request, 'community/createpost.html', {'community': community})


def likes(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
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


def report(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        reason = request.POST['reason']
        request = Reports.objects.create(post=post, reason=reason)
        request.save()
        return HttpResponseRedirect(reverse('community:detailed', args=(post.id,)))
    else:
        return render(request, 'community/report.html', {'post': post})


def seereports(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    report_list = Reports.objects.order_by('-id')
    context = {'report_list': report_list, 'community': community}
    return render(request, 'community/reports.html', context)


def ignorereport(request, reports_id):
    reports = get_object_or_404(Reports, pk=reports_id)
    if not reports:
        return render(request, 'community/reports.html',
                      {'report': reports, 'error_message': "Não foi possivel ignorar"})
    else:
        reports.delete()
        return HttpResponseRedirect(reverse('community:index', args=""))


def deletereports(request, reports_id):
    reports = get_object_or_404(Reports, pk=reports_id)
    post_id = reports.post.id
    post = get_object_or_404(Post, pk=post_id)
    if not post:
        return render(request, 'community/reports.html',
                      {'report': reports, 'error_message': "Não foi possivel apagar o post"})
    else:
        reports.delete()
        post.delete()
        return HttpResponseRedirect(reverse('community:index', args=""))


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


def createcomment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        comment = request.POST['comment']
        creation_data = timezone.now()
        user = request.user
        c = Comment.objects.create(user=user, comment=comment, creation_data=creation_data)
        c.save()
        post.comments.add(c)
        return HttpResponseRedirect(reverse('community:viewpage', args=(post.community.id,)))
    else:
        return render(request, 'community/viewpage.html', {'community_id': post.community.id})


def seerequest(request):
    request_list = Request.objects.order_by('-creation_data')
    context = {'request_list': request_list}
    return render(request, 'community/seerequest.html', context)


def joincommunity(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    utilizador = get_object_or_404(Utilizador, user_id=request.user.id)
    utilizador.communities.add(community)
    return HttpResponseRedirect(reverse('community:index', args=""))


def leavecommunity(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    utilizador = get_object_or_404(Utilizador, user_id=request.user.id)
    utilizador.communities.remove(community)
    return HttpResponseRedirect(reverse('community:index', args=""))


def mycommunities(request):
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


def acceptrequest(request, request_id):
    requestt = get_object_or_404(Request, pk=request_id)
    if not requestt:
        return render(request, 'community/seerequest.html',
                      {'request': requestt, 'error_message': "Não foi possivel aceitar"})
    else:
        name = requestt.name
        image = requestt.image
        user = requestt.user
        creation_data = timezone.now()
        c = Community.objects.create(name=name, image=image, user=user, creation_data=creation_data)
        c.save()
        requestt.delete()
        return HttpResponseRedirect(reverse('community:index', args=""))


def denyrequest(request, request_id):
    requestt = get_object_or_404(Request, pk=request_id)
    if not requestt:
        return render(request, 'community/seerequest.html',
                      {'request': requestt, 'error_message': "Não foi possivel recusar"})
    else:
        requestt.delete()
        return HttpResponseRedirect(reverse('community:index', args=""))
