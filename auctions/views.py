from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import markdown


from .models import User, Category, Listing, Bid, Comment, Watchlist


def index(request):
    active_listings = Listing.objects.filter(is_active=True)
    return render(request, 'auctions/index.html', {
        "active_listings": active_listings,
    })

def closed_listings(request):
    closed_listings = Listing.objects.filter(is_active=False)
    return render(request, 'auctions/closed_listings.html', {
        "closed_listings": closed_listings,
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            messages.success(request, "You have been logged in successfully.")
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.error(request, "Invalid username and/or password.")
            return render(request, "auctions/login.html")
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            messages.error(request, "Passwords must match.")
            return render(request, "auctions/register.html")

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            messages.error(request, "Username already taken.")
            return render(request, "auctions/register.html")
        login(request, user)
        messages.success(request, "You have registered successfully.")
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create_listing(request):
    if request.method == 'POST':
        # Handle form submission
        title = request.POST['title']
        descriptionmd = request.POST['description']
        description = markdown.markdown(descriptionmd)
        starting_bid = request.POST['starting_bid']
        image_url = request.POST['image_url']
        category = request.POST['category']
        user = request.user
        category_data = Category.objects.get(category_name=category)
        listing = Listing(title=title, description=description, starting_bid=float(starting_bid),
                          image_url=image_url, category=category_data, owner=user)
        listing.save()
        messages.success(request, "The listing has been created successfully.")
        return HttpResponseRedirect(reverse(index))
    else:
        all_categories = Category.objects.all()
        # Render form
        return render(request, 'auctions/create_listing.html', {
            "categories": all_categories
        })


def active_listings(request):
    active_listings = Listing.objects.filter(is_active=True)
    context = {'listings': active_listings}
    return render(request, 'auctions/active_listings.html', context)


def listing_detail(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    highest_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()
    current_price = highest_bid.amount if highest_bid else listing.starting_bid
    InWatchList = False
    highest_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()
    highest_bidder = highest_bid.bidder if highest_bid else None

    if request.user.is_authenticated:
        try:
            watchlist = Watchlist.objects.get(user=request.user)
            InWatchList = listing in watchlist.listings.all()
        except Watchlist.DoesNotExist:
            pass
    comments = Comment.objects.filter(listing=listing)
    return render(request, 'auctions/listing_detail.html', {
        "listing": listing,
        "current_price": current_price,
        "InWatchList": InWatchList,
        "comments": comments,
        "highest_bidder": highest_bidder,
    })


@login_required
def add_watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    user = request.user
    watchlist, created = Watchlist.objects.get_or_create(user=user)
    watchlist.listings.add(listing)
    return HttpResponseRedirect(reverse("listing_detail", kwargs={"listing_id": listing_id}))

@login_required
def remove_watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    user = request.user
    watchlist = Watchlist.objects.get(user=user)
    watchlist.listings.remove(listing)
    return HttpResponseRedirect(reverse("listing_detail", kwargs={"listing_id": listing_id}))



@login_required
def watchlist(request):
    watchlist = Watchlist.objects.get(user=request.user)
    listings = watchlist.listings.all()
    return render(request, 'auctions/watchlist.html', {'listings': listings})


@login_required
def add_comment(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    content = request.POST.get("comment")
    Comment.objects.create(content=content, listing=listing, commenter=request.user)
    return HttpResponseRedirect(reverse("listing_detail", args=[listing.id]))


@login_required
def close_listing(request, listing_id):
    # Get the listing object
    listing = Listing.objects.get(pk=listing_id)

    # Determine the winner
    highest_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()
    winner = highest_bid.bidder if highest_bid else None

    # Update the winner field in the listing
    listing.winner = winner
    listing.save()

    # Set the listing to inactive
    listing.is_active = False
    listing.save()

    # Render the listing detail page with a success message
    messages.success(request, 'The listing has been closed.')
    return redirect('listing_detail', listing_id=listing_id)


@login_required
def place_bid(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)

    if request.user == listing.owner:
        messages.error(request, "You can't bid on your own auction.")
        return redirect('listing_detail', listing_id=listing_id)

    if not listing.is_active:
        messages.error(request, 'This auction is closed.')
        return redirect('listing_detail', listing_id=listing_id)

    if request.method == 'POST':
        bid_amount = float(request.POST['bid_amount'])

        if bid_amount < listing.starting_bid:
            messages.error(request, 'Bids must be at least as large as the starting bid.')
            return redirect('listing_detail', listing_id=listing_id)

        if listing.current_price >= bid_amount:
            messages.error(request, 'Your bid must be higher than the current highest bid.')
            return redirect('listing_detail', listing_id=listing_id)

        bid = Bid.objects.create(
            bidder=request.user,
            listing=listing,
            amount=bid_amount
        )

        listing.save()

        messages.success(request, 'Bid placed successfully.')
        return redirect('listing_detail', listing_id=listing_id)
    

def categories(request):
    category_id = request.GET.get('category')
    if category_id:
        category = Category.objects.get(id=category_id)
        listings = Listing.objects.filter(category=category, is_active=True)
    else:
        listings = Listing.objects.filter(is_active=True)
    return render(request, "auctions/categories.html", {
        "active_listings": listings,
        "categories": Category.objects.all(),
    })