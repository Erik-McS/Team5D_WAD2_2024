# User login and logout
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from ratearant.forms import UserForm, ReviewForm, ChangeUserForm, RestaurantForm
from ratearant.models import Restaurant, Cuisine, Review, Comment
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponseForbidden


# Create your views here.


def home(request):
    restaurant_list = Restaurant.objects.order_by('-average_rating')[:5]
    fave_restaurant_list = Restaurant.objects.order_by('-number_of_reviews')[:5]

    context_dict = {'top_message': "Top Rated Restaurants",
                    'fave_message': "Favourite Restaurants",
                    'restaurants': restaurant_list, 'fave_restaurants': fave_restaurant_list,
                    'range': range(1, 6),
                    'isHomePage': True,
                    }
    return render(request, 'ratearant/home.html', context=context_dict)


def about(request):
    context_dict = {'message': 'Placeholder for the Team 5D Rate-A-Rant About page',
                    'isAboutPage': True}
    return render(request, 'ratearant/about.html', context=context_dict)


def food_styles(request):
    restaurants_list = Restaurant.objects.order_by("-cuisine")[:]
    cuisines_list = Cuisine.objects.order_by("-cuisineName")[:]

    context_dict = {
        "cuisines": cuisines_list,
        "restaurants": restaurants_list,
        'range': range(1, 6)
    }
    return render(request, 'ratearant/food_styles.html', context=context_dict)


def categories(request, cuisineName):
    context_dict = {}
    try:
        # Assuming cuisineName is a valid name of a cuisine
        cuisine = Cuisine.objects.get(cuisineName=cuisineName)
        restaurants = Restaurant.objects.filter(cuisine=cuisine)

        context_dict = {
            "cuisine": cuisine,
            "restaurants": restaurants
        }

    except Cuisine.DoesNotExist:
        context_dict = {
            "cuisine": None,
            "restaurants": []
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
    fave_restaurant_list = Restaurant.objects.order_by('-number_of_reviews')

    context_dict = {'top_message': "Top Rated Restaurants",
                    'fave_message': "Favourite Restaurants",
                    'restaurants': restaurant_list,
                    'fave_restaurants': fave_restaurant_list,
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
            review.foodRating = request.POST.get('foodRating')
            review.serviceRating = request.POST.get('serviceRating')
            review.overallRating = request.POST.get('overallRating')
            review.averageScore = (int(review.foodRating) + int(review.serviceRating) + int(review.overallRating)) / 3
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
def edit_profile(request):
    if request.method == 'POST':
        # Initialize the form with POST data and the current user instance
        user_form = ChangeUserForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user = user_form.save(commit=False)

            # Directly update the user object fields from form.cleaned_data
            user.first_name = user_form.cleaned_data['first_name']
            user.last_name = user_form.cleaned_data['last_name']

            # Update the password only if a new one is provided
            if 'password' in user_form.cleaned_data and user_form.cleaned_data['password']:
                user.set_password(user_form.cleaned_data['password'])
                update_session_auth_hash(request, user)  # Keep the user logged in

            user.save()
            messages.success(request, 'Your profile was successfully updated.')
            return redirect('ratearant:edit_profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        # Pre-fill the form with the current user instance on GET requests
        user_form = ChangeUserForm(instance=request.user)

    return render(request, 'ratearant/edit_profile.html', {'user_form': user_form})

@login_required
def my_comments(request):
    comments = Review.objects.all()
    reviews = []
    for eachComment in comments:
        if eachComment.user == request.user:
            reviews.append(eachComment)
    return render(request, 'ratearant/my_comments.html', {'comments': reviews})

@login_required
def delete_comment(request, reviewId):
    comments = Review.objects.all()
    for eachComments in comments:
        if eachComments.reviewId == reviewId and eachComments.user == request.user:
            eachComments.delete()
            break
    return redirect('ratearant:my_comments')

@login_required
def add_restaurant(request):
    if request.method == 'POST':
        form = RestaurantForm(request.POST)
        if form.is_valid():
            request.session['form_data'] = request.POST
            return redirect('ratearant:thank_you')
    else:
        form = RestaurantForm()
    return render(request, 'ratearant/add_restaurant.html', {'form': form})

@login_required
def thank_you(request):
    form_data = request.session.get('form_data')
    if form_data:
        del request.session['form_data']
    return render(request, 'ratearant/thank_you.html', {'form_data': form_data})
