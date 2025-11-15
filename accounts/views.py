from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

def register_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm = request.POST['confirm']

        if password == confirm:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already taken!')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                messages.success(request, 'Account created successfully!')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match!')
    return render(request, 'accounts/register.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')  # this will be our fitness page later
        else:
            messages.error(request, 'Invalid username or password!')
    return render(request, 'accounts/login.html')

def logout_user(request):
    logout(request)
    return redirect('login')
from django.shortcuts import render