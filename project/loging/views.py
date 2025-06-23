from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache, cache_control
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render
from product.models import Product, Category, Brand


from .tokens import email_token_generator

User = get_user_model()




from random import sample

def index(request):
    categories = Category.objects.all()
    brands = Brand.objects.all()
    products = Product.objects.all()[:3]

    random_brands = sample(list(brands), min(len(brands), 5))  # Show up to 5 random brands

    return render(request, 'index.html', {
        'categories': categories,
        'brands': brands,
        'products': products,
        'random_brands': random_brands,
    })


@login_required(login_url='signin')
@never_cache
def home1(request):
    return render(request, 'home1.html')


@never_cache
def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        name = request.POST['name']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('signup')
        if pass1 != pass2:
            messages.error(request, "Passwords didn't match.")
            return redirect('signup')

        user = User.objects.create_user(username, email, pass1)
        user.first_name = name
        user.is_active = False
        user.save()

        current_site = get_current_site(request)
        subject = "Activate Your Account"
        message = render_to_string('loging/email_verification.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': email_token_generator.make_token(user),
        })
        email_message = EmailMessage(subject, message, to=[email])
        email_message.content_subtype = "html"
        email_message.send()

        messages.success(request, "Account created! Check your email to verify your account.")
        return redirect('signin')

    return render(request, 'loging/signup.html')


@never_cache
def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        user = authenticate(username=username, password=pass1)

        if user is not None:
            if user.is_superuser:
                login(request, user)
                return redirect("member")
            elif user.is_active:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name}")
                return redirect('product')
            else:
                messages.error(request, "Account not activated. Please check your email.")
        else:
            messages.error(request, "Invalid username or password.")
        return redirect('signin')

    return render(request, 'loging/signin.html')


@login_required(login_url='signin')
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def signout(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('signin')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and email_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return HttpResponse('Email verified successfully! You can now <a href="/signin/">login</a>.')
    else:
        return HttpResponse('Activation link is invalid!')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        user = User.objects.filter(email=email).first()

        if user:
            current_site = get_current_site(request)
            subject = 'Reset Your Password'
            message = render_to_string('loging/password_reset_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            email_message = EmailMessage(subject, message, to=[email])
            email_message.content_subtype = "html"
            email_message.send()

            messages.success(request, "Password reset link sent to your email.")
            return redirect('signin')
        else:
            messages.error(request, "No user found with this email.")
            return redirect('forgot_password')

    return render(request, 'loging/forgot_password.html')


def reset_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST['password']
            confirm_password = request.POST['confirm_password']
            if password == confirm_password:
                user.set_password(password)
                user.save()
                messages.success(request, "Password reset successful.")
                return redirect('signin')
            else:
                messages.error(request, "Passwords do not match.")
        return render(request, 'loging/reset_password.html', {'validlink': True})
    else:
        messages.error(request, "Invalid or expired reset link.")
        return render(request, 'loging/reset_password.html', {'validlink': False})
