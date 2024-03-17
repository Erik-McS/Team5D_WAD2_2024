from django.db import models

# user login and logout
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify


# Create your models here.

# Table for the cuisine type.
class Cuisine(models.Model):
    cuisineId = models.AutoField(primary_key=True)
    cuisineName = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.cuisineName


# Table for the restaurant.
class Restaurant(models.Model):
    restaurantId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128, unique=True)
    address = models.CharField(max_length=256)
    phone = models.CharField(max_length=16)
    website = models.URLField()
    openingTime = models.CharField(max_length=30)
    priceRange = models.CharField(max_length=16)
    cuisine = models.ForeignKey(Cuisine, on_delete=models.CASCADE)
    #your_top_rated_restaurants for user
    # imgpath=models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    #Score
    number_of_reviews = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Restaurant, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


# Table for the user.
class User(models.Model):
    userId = models.AutoField(primary_key=True)
    username = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    firstName = models.CharField(max_length=128)
    lastName = models.CharField(max_length=128)

    def __str__(self):
        return self.username


# Table for the reviews.
class Review(models.Model):
    reviewId = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    message = models.TextField()
    likes = models.IntegerField(default=0)
    averageScore = models.DecimalField(max_digits=3, decimal_places=1)
    foodRating = models.IntegerField()
    serviceRating = models.IntegerField()
    overallRating = models.IntegerField()

    def __str__(self):
        return str(self.reviewId)


# Table for the comments on reviews.
class Comment(models.Model):
    commentId = models.AutoField(primary_key=True)
    review = models.ForeignKey(Review, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    likes = models.IntegerField(default=0)

    def __str__(self):
        return str(self.reviewId)


# Table for the scores given by users.
class Score(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    foodRating = models.IntegerField()
    serviceRating = models.IntegerField()
    overallRating = models.IntegerField()

    def __str__(self):
        return self.review


# Table for the User Profile
class UserProfile(models.Model):
    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # The additional attributes we wish to include.
    firstName = models.CharField(max_length=128)
    lastName = models.CharField(max_length=128)
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    def __str__(self):
        return self.user.username


class TopRatedRestaurant(models.Model):
    name = models.CharField(max_length=255)
    image_url = models.URLField()

    def __str__(self):
        return self.name


class YourTopRatedRestaurant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    image_url = models.URLField()

    def __str__(self):
        return self.name


