from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required


# Create your views here.
from .forms import SignupForm

def home(request):
    context={
        'title':'homepage',
    }
    return render(request,'index.html',context)

def signup(request):
    #Check if user is authenticated
    if request.user.is_authenticated:
        return redirect('dashbord')
    else:
        # Perform the signup
        form=SignupForm()
        if request.method=="POST":
            form=SignupForm(request.POST)
            if form.is_valid:
                form.save()
                user=form.cleaned_data.get('username')
                messages.success(user + "account created successfully")
                return redirect('login')
            
            else:
                print(form.errors)

        context={
            'title': 'signup',
            'form': form
        }
    return render(request,'signup.html', context)

def loginUser(request):
    # Check if user is authenticated
    if request.user.is_authenticated:
        return redirect('dashbord')
    else:
        context={
            'title':'login'
        }
        if request.method=="POST":
            # Getting username and password from the form
            username=request.POST.get('username')
            password=request.POST.get('password')

            # Checking if user is authenticated
            user=authenticate(request, username=username, password=password)

            # Check if user is in the available
            if user is not None:
                login(request, user)
                return redirect('dashbord')
            else:
                messages.info('incorrect username or password ')


            context={
                'title':'login'
            }
    return render(request,'login.html', context)

# Handling user logout
def logoutUser(request):
    logout(request)
    return redirect('login')
@login_required(login_url='login')
def dashbord(request):
    context={
        'title':'dashboard',
    }
    return render(request, 'dashbord.html', context)