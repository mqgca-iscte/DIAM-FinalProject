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
    communities_list = Community.objects.order_by('-creation_data')[:5]
    context = {'communities_list': communities_list}
    return render(request, 'community/index.html', context)


def viewpage(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    return render(request, 'community/viewpage.html', {'community': community})


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
            omeuuser = User.objects.create_user(username, email, password)
            utilizador = Utilizador(user=omeuuser)
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
    communities_list = Community.objects.order_by('-creation_data')[:5]
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
                r = Request.objects.create(name=filename, image=image,
                                           user=user, creation_data=creation_data)
                r.save()
                return HttpResponseRedirect(reverse('community:index', args=""))
    else:
        return render(request, 'community/createrequest.html', {})


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
            return render(request, 'community/viewpage.html', {'community': community})
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
        return HttpResponseRedirect(reverse('community:detailed', args=(post.id,)))
    else:
        return HttpResponseRedirect(reverse('community:index', args=""))


def report(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        reason = request.POST['reason']
        request = Reports.objects.create(post=post, reason=reason)
        request.save()
        return HttpResponseRedirect(reverse('community:detailed', args=(post.id,)))
    else:
        return render(request, 'community/report.html', {'post': post})


def seereports(request):
    reports_list = Reports.objects.order_by('-id')[:5]
    context = {'reports_list': reports_list}
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


def detailed(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments_list = post.comments.all()
    return render(request, 'community/detailed.html', {'post': post, 'comments_list': comments_list})


def createcomment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        comment = request.POST['comment']
        creation_data = timezone.now()
        user = request.user
        c = Comment.objects.create(user=user, comment=comment, creation_data=creation_data)
        c.save()
        post.comments.add(c)
        return HttpResponseRedirect(reverse('community:detailed', args=(post.id,)))
    else:
        return render(request, 'community/detailed.html', {'post': post})


def seerequest(request):
    request_list = Request.objects.order_by('-creation_data')[:5]
    context = {'request_list': request_list}
    return render(request, 'community/seerequest.html', context)


def joincommunity(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    user_id = request.session.get('user_id')
    utilizador = get_object_or_404(Utilizador, user_id=user_id)
    utilizador.communities.add(community)
    return HttpResponseRedirect(reverse('community:index', args=""))


def mycommunities(request):
    user_id = request.session.get('user_id')
    utilizador = get_object_or_404(Utilizador, user_id=user_id)
    communities_list = utilizador.communities.all()
    context = {'communities_list': communities_list}
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
