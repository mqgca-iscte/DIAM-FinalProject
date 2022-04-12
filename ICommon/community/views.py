from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.shortcuts import render

from .models import Community, Post, Utilizador


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
