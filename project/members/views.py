from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

# Create your views here.


def signout(request):
    logout(request)
    messages.success(request, "loged out successfully!")
    return redirect('signin')


@login_required(login_url='signin')
@never_cache
def member(request):
    mem=User.objects.all()
    return render(request,'members/meber.html',{'mem':mem})


@login_required(login_url='signin')
@never_cache
def add(request):
    return render(request,'members/add.html')

def addrec(request):
    
    x=request.POST['username']
    y=request.POST['email']
    z=request.POST['password']
    
    if User.objects.filter(username=x):
        messages.error(request, "user name already exist! please enther other username")
        return redirect('add')

    elif User.objects.filter(email=y):
        messages.error(request, "email already registered!")
        return redirect('add')
    else:
        mem=User(username=x,email=y)
        mem.set_password(z)
        mem.save()
        return redirect('member')


def delete(request,id):
    mem=User.objects.get(id=id)
    mem.delete()
    return redirect("member")


@login_required(login_url='signin')
@never_cache
def update(request,id):
    mem=User.objects.get(id=id)
    return render(request,'members/update.html',{'mem':mem})


def uprec(request,id):
    x=request.POST['username']
    y=request.POST['email']
    mem=User.objects.get(id=id)
    mem.username=x
    mem.email=y
    mem.save()
    return redirect('member')
# Create your views here.

def oderde(request):
    return render(request,'product/oderde.html')