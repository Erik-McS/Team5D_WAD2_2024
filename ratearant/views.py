from django.shortcuts import render

#User login and logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponse
from ratearant.forms import UserForm

# Create your views here.


def home(request):
    context_dict = {'message': 'Placeholder for the Team 5D Rate-A-Rant homepage',
                    'isHomePage': True}
    return render(request, 'ratearant/home.html', context=context_dict)


def about(request):
    context_dict = {'message': 'Placeholder for the Team 5D Rate-A-Rant About page',
                    'isAboutPage': True}
    return render(request, 'ratearant/about.html', context=context_dict)
    
#User login
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('ratearant:home'))
            else:
                return HttpResponse("Your user account is disabled.")
    else:
        return render(request, 'ratearant/login.html')

#User logout
@login_required
def user_logout(request):
    logout(request)
    return redirect('ratearant:home')

def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(request.POST)

        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password (user_form.cleaned_data['password'])
            user.email = user_form.cleaned_data['email']
            user.first_name  = user_form.cleaned_data['first_name']
            user.last_name  = user_form.cleaned_data['last_name']
            user.save()
            registered = True
        else:
            print(user_form.errors)

    else:
        user_form = UserForm()
    return render(request, 
                  'ratearant/register.html', 
                  context = {'user_form': user_form, 
                             'registered': registered})