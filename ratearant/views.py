# User login and logout
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from ratearant.forms import RestaurantForm, UserForm, ReviewForm, ChangeUserForm
from ratearant.models import Restaurant, Cuisine, Review
from django.contrib import messages
from decimal import Decimal


# home page
def home(request):
    # getting the top rated and favourite restaurants
    restaurant_list = Restaurant.objects.order_by('-average_rating')[:5]
    fave_restaurant_list = Restaurant.objects.order_by('-number_of_reviews')[:5]

    context_dict = {'top_message': "Top Rated Restaurants",
                    'fave_message': "Favourite Restaurants",
                    'restaurants': restaurant_list,
                    'fave_restaurants': fave_restaurant_list,
                    'range': range(1, 6),  # number of stars to display
                    'isHomePage': True,  # to display the home page nav bar
                    }
    return render(request, 'ratearant/home.html', context=context_dict)


# about page
def about(request):
    context_dict = {'message': 'Placeholder for the Team 5D Rate-A-Rant About page',
                    'isAboutPage': True  # to display the about page nav bar
                    }
    return render(request, 'ratearant/about.html', context=context_dict)


# food styles page
def food_styles(request):
    # getting the cuisines and restaurants by order
    restaurants_list = Restaurant.objects.order_by("-cuisine")[:]
    cuisines_list = Cuisine.objects.order_by("-cuisineName")[:]

    context_dict = {
        "cuisines": cuisines_list,
        "restaurants": restaurants_list,
        'range': range(1, 6)  # number of stars to display
    }
    return render(request, 'ratearant/food_styles.html', context=context_dict)


# categories page
def categories(request, cuisineName):
    context_dict = {}
    try:
        # Assuming cuisineName is a valid name of a cuisine
        cuisine = Cuisine.objects.get(cuisineName=cuisineName)
        restaurants = Restaurant.objects.filter(cuisine=cuisine)

        context_dict = {
            "cuisine": cuisine,
            "restaurants": restaurants,
            'range': range(1, 6)  # number of stars to display
        }
    # If cuisine does not exist, return an empty list
    except Cuisine.DoesNotExist:
        context_dict = {
            "cuisine": None,
            "restaurants": []
        }
    return render(request, 'ratearant/categories.html', context=context_dict)


# restaurant page
def show_restaurant(request, restaurant_name_slug):
    context_dict = {}

    try:
        # getting the restaurant records by the slug
        restaurant = Restaurant.objects.get(slug=restaurant_name_slug)
        # getting the reviews associated with the restaurant
        reviews = Review.objects.filter(restaurant=restaurant)
        context_dict = {'restaurant': restaurant,
                        'name': restaurant.name,
                        'address': restaurant.address,
                        'phone': restaurant.phone,
                        'website': restaurant.website,
                        'openingTime': restaurant.openingTime,
                        'priceRange': restaurant.priceRange,
                        'cuisine': restaurant.cuisine,
                        'reviews': reviews,
                        'reviewed': False, }
        # Check if the user has already reviewed the restaurant
        if request.user.is_authenticated:
            if Review.objects.filter(user=request.user, restaurant_id=restaurant.restaurantId).exists():
                context_dict['reviewed'] = True
        else:
            context_dict['reviewed'] = False
        # If restaurant does not exist, return an empty list
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


# User login view
def login_view(request):
    error_message = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        # Check if the user is valid
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(reverse('ratearant:home'))
        else:
            error_message = 'Invalid username or password'

    context = {
        'error_message': error_message
    }

    return render(request, 'ratearant/login.html', context)


# User logout view
@login_required
def user_logout(request):
    logout(request)
    return redirect('ratearant:home')


# User registration page
def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        # Check if the form is valid
        if user_form.is_valid():
            # Save the user
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.email = user_form.cleaned_data['email']
            user.first_name = user_form.cleaned_data['first_name']
            user.last_name = user_form.cleaned_data['last_name']
            user.save()
            registered = True

            # Authenticate the user and login
            login(request, user)
        else:
            print(user_form.errors)

    else:
        user_form = UserForm()
    return render(request,
                  'ratearant/register.html',
                  context={'user_form': user_form,
                           'registered': registered})


# trending page
def trending(request):
    # getting the top rated and favourite restaurants
    restaurant_list = Restaurant.objects.order_by('-average_rating')[:5]
    fave_restaurant_list = Restaurant.objects.order_by('-number_of_reviews')

    context_dict = {'top_message': "Top Rated Restaurants",
                    'fave_message': "Favourite Restaurants",
                    'restaurants': restaurant_list,
                    'fave_restaurants': fave_restaurant_list,
                    'range': range(1, 6)  # number of stars to display
                    }
    return render(request, 'ratearant/trending.html', context=context_dict)


# add review page
@login_required
def add_review(request, restaurant_name_slug):
    restaurant = Restaurant.objects.get(slug=restaurant_name_slug)
    # Check if the user has already reviewed the restaurant
    if Review.objects.filter(user=request.user, restaurant_id=restaurant.restaurantId).exists():
        return render(request, 'ratearant/add_review.html', {'reviewed': True})
    # If the user has not reviewed the restaurant, proceed to add a review
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        # Check if the form is valid
        if form.is_valid():
            # Save the review
            review = form.save(commit=False)
            review.user = request.user
            review.restaurant = restaurant
            review.foodRating = request.POST.get('foodRating')
            review.serviceRating = request.POST.get('serviceRating')
            review.overallRating = request.POST.get('overallRating')
            # Calculate the average score
            review.averageScore = (
                                          int(review.foodRating) +
                                          int(review.serviceRating) +
                                          int(review.overallRating)
                                  ) / 3

            review.save()

            # Update the restaurant's average rating and number of reviews
            restaurant.average_rating = (restaurant.average_rating * restaurant.number_of_reviews +
                                         Decimal(review.averageScore)) / (restaurant.number_of_reviews + 1)
            restaurant.number_of_reviews = restaurant.number_of_reviews + 1
            restaurant.save()
            return redirect('ratearant:show_restaurant', restaurant_name_slug=restaurant.slug)
    else:
        form = ReviewForm()

    # If the request method is not POST, display the form
    context = {
        'form': form,
        'restaurant': restaurant
    }
    return render(request, 'ratearant/add_review.html', context)


# edit profile page
@login_required
def edit_profile(request):
    # Initialize the form with the current user instance
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


# my comments page
@login_required
def my_comments(request):
    # getting the user's comments
    comments = Review.objects.all()
    reviews = []
    # Filtering the comments to get only the user's comments
    for eachComment in comments:
        if eachComment.user == request.user:
            # Adding the comments to the list
            reviews.append(eachComment)
    return render(request, 'ratearant/my_comments.html', {'comments': reviews})


# delete comment page
@login_required
def delete_comment(request, reviewId):
    # getting the user's comments
    comments = Review.objects.all()
    # Filtering the comments to get only the user's comments
    for eachComments in comments:
        # if eachComments.user == request.user:
        if eachComments.reviewId == reviewId and eachComments.user == request.user:
            # updating the restaurant's average rating and number of reviews
            restaurant = eachComments.restaurant
            restaurant.average_rating = (
                                        restaurant.average_rating * restaurant.number_of_reviews - eachComments.overallRating) / (
                                        restaurant.number_of_reviews - 1)
            restaurant.number_of_reviews = restaurant.number_of_reviews - 1
            restaurant.save()
            # deleting the comment
            eachComments.delete()
            break
    return redirect('ratearant:my_comments')


# add restaurant page
@login_required
def add_restaurant(request):
    # Check if the user is an admin
    if request.method == 'POST':
        # Initialize the form with POST data
        form = RestaurantForm(request.POST)
        # Check if the form is valid
        if form.is_valid():
            # Save the restaurant
            review = form.save(commit=False)
            review.user = request.user
            review.name = request.POST.get('name')
            review.address = request.POST.get('address')
            review.website = request.POST.get('website')
            review.cuisine = Cuisine.objects.get(cuisineId=request.POST.get('cuisine'))
            review.save()
            
            request.session['form_data'] = request.POST
            return redirect('ratearant:thank_you')
    else:
        form = RestaurantForm()
    return render(request, 'ratearant/add_restaurant.html', {'form': form})


# thank you page
@login_required
def thank_you(request):
    # Check if the user is an admin
    form_data = request.session.get('form_data')
    if form_data:
        del request.session['form_data']
    return render(request, 'ratearant/thank_you.html', {'form_data': form_data})
