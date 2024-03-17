# User login and logout
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse

from ratearant.forms import UserForm, ReviewForm
from ratearant.models import Restaurant, Cuisine, Review
from ratearant.models import TopRatedRestaurant, YourTopRatedRestaurant


# Create your views here.


def home(request):
    restaurant_list = Restaurant.objects.order_by('-average_rating')[:5]
    fave_restaurant_list = Restaurant.objects.order_by('-number_of_reviews')[5:]

    context_dict = {'top_message': "Top Rated Restaurants",
                    'fave_message': "Favourite Restaurants",
                    'restaurants': restaurant_list, 'fave_restaurants': fave_restaurant_list,
                    'range': range(1, 6)
                    }
    return render(request, 'ratearant/home.html', context=context_dict)


def about(request):
    context_dict = {'message': 'Placeholder for the Team 5D Rate-A-Rant About page',
                    'isAboutPage': True}
    return render(request, 'ratearant/about.html', context=context_dict)


def categories(request):
    restaurants_list = Restaurant.objects.order_by("-cuisine")[:]
    cuisines_list = Cuisine.objects.order_by("-cuisineName")[:]

    context_dict = {
        "cuisines": cuisines_list,
        "restaurants": restaurants_list,
        'range': range(1, 6)
    }
    return render(request, 'ratearant/categories.html', context=context_dict)


def show_restaurant(request, restaurant_name_slug):
    context_dict = {}

    try:
        # getting the restaurant records by the slug
        restaurant = Restaurant.objects.get(slug=restaurant_name_slug)
        # getting the reviews associated with the restaurant
        reviews = Review.objects.filter(restaurant=restaurant)
        context_dict = {'restaurant': restaurant, 'name': restaurant.name,
                        'address': restaurant.address,
                        'phone': restaurant.phone,
                        'website': restaurant.website,
                        'openingTime': restaurant.openingTime,
                        'priceRange': restaurant.priceRange,
                        'cuisine': restaurant.cuisine,
                        'reviews': reviews}


    except Restaurant.DoesNotExist:
        context_dict['restaurant'] = None
        context_dict['name'] = None
        context_dict['address'] = None
        context_dict['phone'] = None
        context_dict['website'] = None
        context_dict['openingTime'] = None
        context_dict['priceRange'] = None
        context_dict['cuisine'] = None
        context_dict['reviews'] = None

    return render(request, 'ratearant/restaurant.html', context=context_dict)


# User login
def login_view(request):
    error_message = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(reverse('ratearant:home'))

    context = {
        'error_message': error_message
    }

    return render(request, 'ratearant/login.html', context)


# User logout
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
            user.set_password(user_form.cleaned_data['password'])
            user.email = user_form.cleaned_data['email']
            user.first_name = user_form.cleaned_data['first_name']
            user.last_name = user_form.cleaned_data['last_name']
            user.save()
            registered = True
        else:
            print(user_form.errors)

    else:
        user_form = UserForm()
    return render(request,
                  'ratearant/register.html',
                  context={'user_form': user_form,
                           'registered': registered})


def trending(request):
    restaurant_list = Restaurant.objects.order_by('-average_rating')[:5]
    fave_restaurant_list = Restaurant.objects.order_by('-number_of_reviews')[:5]

    user_top_rated_restaurants = None
    if request.user.is_authenticated:
        user_top_rated_restaurants = YourTopRatedRestaurant.objects.filter(user=request.user)


    context_dict = {
        'top_message': "Top Rated Restaurants",
        'fave_message': "Favourite Restaurants",
        'restaurants': restaurant_list,
        'fave_restaurants': fave_restaurant_list,
        'user_top_rated_restaurants': user_top_rated_restaurants,
        'range': range(1, 6)
    }
    return render(request, 'ratearant/trending.html', context=context_dict)


@login_required
def add_review(request, restaurant_name_slug):
    restaurant = Restaurant.objects.get(slug=restaurant_name_slug)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.restaurant = restaurant
            review.save()
            return redirect('ratearant:show_restaurant', restaurant_name_slug=restaurant.slug)
    else:
        form = ReviewForm()

    context = {
        'form': form,
        'restaurant': restaurant
    }
    return render(request, 'ratearant/add_review.html', context)


@login_required
def like_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    user_like, created = UserLike.objects.get_or_create(user=request.user, restaurant=restaurant)

    if not created:
        # User has already liked the restaurant, so remove the like
        user_like.delete()
        restaurant.likes -= 1
    else:
        # User has liked the restaurant
        restaurant.likes += 1

    restaurant.save()
    return redirect('restaurant_detail', restaurant_id=restaurant_id)