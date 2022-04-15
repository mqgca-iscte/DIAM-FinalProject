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

from .models import Community, Post, Utilizador, Request


def index(request):
    communities_list = Community.objects.order_by('-creation_data')[:5]
    context = {'communities_list': communities_list}
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
                c = Community.objects.create(name=name, image=uploaded_file_url, creation_data=creation_data)
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
                if request.session.get('user_id') is not None:
                    user_id = request.session.get('user_id')
                    utilizador = get_object_or_404(Utilizador, user_id=user_id)
                    pedido = Request.objects.create(name=name, image=image, user=utilizador,
                                                    creation_data=creation_data)
                    pedido.save()
                    return render(request, 'community/index.html', {})
    else:
        return render(request, 'community/createrequest.html', {})


def seerequest(request):
    request_list = Request.objects.order_by('-creation_data')[:5]
    context = {'request_list': request_list}
    return render(request, 'community/seerequest.html', context)


def acceptrequest(request, request_id):
    requestt = get_object_or_404(Request, pk=request_id)
    if not requestt:
        return render(request, 'community/seerequest.html',
                      {'request': requestt, 'error_message': "Não foi possivel aceitar"})
    else:
        name = requestt.name
        image = requestt.image
        creation_data = timezone.now()
        c = Community.objects.create(name=name, image=image, creation_data=creation_data)
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
