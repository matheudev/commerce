from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name

class Listing(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.CharField(max_length=1000)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="category")
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user")
    winner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='won_listings')

    @property
    def current_price(self):
        highest_bid = Bid.objects.filter(listing=self).order_by('-amount').first()
        return highest_bid.amount if highest_bid else self.starting_bid
    
    def __str__(self):
        return self.title

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.commenter} comment on {self.listing}"
    

class Watchlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    listings = models.ManyToManyField(Listing, blank=True)

    def __str__(self):
        return f"Watchlist of {self.user.username}"