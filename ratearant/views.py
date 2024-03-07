from django.shortcuts import render
from ratearant.models import Restaurant


# Create your views here.


def home(request):
    restaurant_list = Restaurant.objects.order_by('-name')[:5]
    restaurant_list2 = Restaurant.objects.order_by('name')[5:]

    context_dict = {}
    context_dict['top_message'] = 'Top Rated Restaurants'
    context_dict['fave_message'] = 'Favourite Restaurants'
    context_dict['restaurants'] = restaurant_list
    context_dict['fave_restaurants'] = restaurant_list2
    return render(request, 'ratearant/home.html', context=context_dict)


def about(request):
    context_dict = {'message': 'Placeholder for the Team 5D Rate-A-Rant About page',
                    'isAboutPage': True}
    return render(request, 'ratearant/about.html', context=context_dict)


def register(request):
    context_dict = {'message': 'Placeholder for the Team 5D Rate-A-Rant Register page'}
    return render(request, 'ratearant/register.html', context=context_dict)


def login(request):
    context_dict = {'message': 'Placeholder for the Team 5D Rate-A-Rant Login page'}
    return render(request, 'ratearant/login.html', context=context_dict)
