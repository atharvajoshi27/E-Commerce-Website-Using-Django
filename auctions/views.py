from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
# import requests

from .models import User, Listing, Bids, Category, Watchlist, Comment
from .forms import CreateListing
import re

DEFAULT_CATEGORY = Category.objects.filter(category="No Category").first()

def index(request):
    context = {
        "title" : "index",
        "listings" : Listing.objects.filter(active=True).all(),
    }
    return render(request, "auctions/index.html", context)

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def process(category): # Function used in createlisting
    category = category.strip()
    category = re.sub(r"\s+", " ", category)
    category = category.capitalize()
    return category


def createlisting(request):
    if request.method == "POST":
        print("IM HERE")
        form = CreateListing(request.POST, request.FILES)
        if form.is_valid():
            print("DONE MAN NO PROBLEM!")
            instance = form.save(commit=False)
            instance.creator = request.user
            instance.number_of_bids = 0
            ###
            category = instance.category
            if category is None:
                category_belongs = DEFAULT_CATEGORY
            else:
                # category = category.strip()
                # category = re.sub(r"\s+", " ", category)
                # category = category.lower().capitalize()
                category = process(category)
                category_belongs = Category.objects.filter(category=category).first()
                if category_belongs is None:
                    new_category = Category(category=category.capitalize())
                    new_category.save()
                    category_belongs = new_category
            instance.category_belongs = category_belongs
            instance.save()
            category_belongs.entries += 1
            category_belongs.save()
            ####
            # title = form.cleaned_data.get('title')
            # description = form.cleaned_data.get('description')
            # starting_bid = form.cleaned_data.get('starting_bid')
            # category = form.cleaned_data.get('category')
            # image_file = form.cleaned_data.get('image_file')
            # image_url = form.cleaned_data.get('image_url')
            # creator = request.user
            # l = Listing(title=title, description=description, starting_bid=starting_bid, category=category, image_file=image_file, image_url=image_url, creator=creator)
            # l.save()
            context = {
                "title" : "Info Listing",
                "listing" : instance,
            }
            
            return HttpResponseRedirect(reverse('showlisting', args=[instance.id]))
            # return index(request, instance.id)
            # return redirect('index', id=instance.id)
            # return HttpResponseRedirect(index(request, instance.id))
            # return render(request, "auctions/showlisting.html", context) 
        else:
            print (form.errors)
            raise Http404(f'Validation Error in CreateListing Form! : {form.errors}')
    else:
        form = CreateListing()
        context = {
            "title" : "Create New Listing",
            "form" : form,
        }
        return render(request, "auctions/createlisting.html", context)

@login_required
def placebid(request):
    if request.method == "POST":
        try :
            bidvalue = request.POST.get('bid')
            id = request.POST.get('listing')
            listing = Listing.objects.filter(pk=id).first()
            if int(bidvalue) <= listing.max_bid:
                messages.error(request, f"Bid value must be greater than {listing.max_bid}", extra_tags='danger')
                return HttpResponseRedirect(reverse("showlisting", args=[listing.id]))
            bid = Bids(price=bidvalue, maker=request.user, listing=listing)
            bid.save()
            listing.number_of_bids += 1
            listing.max_bid = bidvalue
            listing.bid_owner_id = request.user.id
            listing.save()
            context = {
                "title" : "Info Listing",
                "listing" : listing,
            }
        except Exception as e:
            id = None
            context = {
                "title" : "Error",
                "listing" : [],
            }
            messages.error(request, f"Something Went Wrong!{e}", extra_tags='danger')
            
        # messages.success(request, f"Bid placed successfully!", extra_tags='danger')
        messages.success(request, f"Bid placed successfully!")
        return HttpResponseRedirect(reverse("showlisting", args=[listing.id]))
    else:
        raise Http404("Requested page isn't available")


def showlisting(request, id):
    listing = Listing.objects.filter(id=id).first()
    if listing is None:
        raise Http404("Page Not Found!")           
    context = {
        "title" : listing.title,
        "listing" : listing,
    }
    return render(request, "auctions/showlisting.html", context)
    # if (request.method == "POST") or (myid != None):
    #     if myid == None:
    #         id = request.POST.get('id')
    #     else:
    #         id = myid
    #         myid = None
    #     # print(listing.title)
    #     # print(oxbj)
    #     context = {
    #         # "title" : "Info Listing",
    #         "title" : "I am in index yeah!",
    #         "listing" : listing,
    #     }
    # else:
    #     raise Http404("Not Allowed")
####
def categorywise(request, category):
    category_belongs = Category.objects.filter(category=category).first()
    if category_belongs is None:
        raise Http404("No Category Found!")
    else :
        listings = category_belongs.listing_set.filter(active=True).all()
        context = {
            "listings" : listings,
            "title" : f"Listings for {category}",
        }
        return render(request, "auctions/index.html", context)

def categories(request):
    categorylist = Category.objects.all()
    context = {
        "title" : "Categories",
        "categorylist" : categorylist,
    }
    return render(request, "auctions/categories.html", context)
####

def addtowatchlist(request):
    if request.method == "POST":
        listingid = request.POST.get('listing')
        about = request.POST.get('about')
        listing = Listing.objects.filter(id=listingid).first()
        user = request.user
        try:
            watchlist = user.watchlist
            if about == "1":
                watchlist.items.add(listing)
                watchlist.number += 1
            if about == "-1":
                watchlist.items.remove(listing)
                watchlist.number -= 1
            watchlist.save()
        except ObjectDoesNotExist:
            watchlist = Watchlist(user=user)
            watchlist.save()
            watchlist.items.add(listing)
            watchlist.number += 1
            watchlist.save()
        return redirect('showlisting', id=listing.id)
    else :
        return HttpResponse("Not post")

@login_required
def watchlist(request):
    try:
        watchlist = request.user.watchlist.items.all()
    except ObjectDoesNotExist:
        watchlist = []
    context = {
        "title" : "Watchlist",
        "watchlist" : watchlist,
    }
    return render(request, "auctions/watchlist.html", context)
    # return HttpResponse("Work in progress!")

@login_required
def comment(request):
    if request.method == "POST":
        try :
            comment = request.POST.get('comment')
            id = request.POST.get('listing')
            listing = Listing.objects.filter(pk=id).first()
            comment = Comment(comment=comment, listing=listing, commenter=request.user)
            comment.save()
            listing.ncomments += 1
            listing.save()
            context = {
                "title" : "Comment",
                "listing" : listing,
            }
        except Exception as e:
            id = None
            context = {
                "title" : "Error",
                "listing" : [],
            }
            
            messages.error(request, f"Something Went Wrong!", extra_tags='danger')
        return HttpResponseRedirect(reverse("showlisting", args=[listing.id]))
        # return render(request, "auctions/showlisting.html", context)
    else:
        raise Http404("Requested page isn't available")

def userlistings(request, name):
    user = User.objects.filter(username=name).first()
    listings = user.listing_set.filter(active=True).all()
    context = {
        "title" : "Listings",
        "listings" : listings,
    }
    return render(request, "auctions/index.html", context)

def deactivate(request, title):
    if request.method == "POST":
        listingid = request.POST.get('listing')
        listing = Listing.objects.filter(id=listingid).first()
        listing.active = False
        if listing.category == None:
            category = 'No Category'
        else:
            category = process(listing.category)        
        category = Category.objects.filter(category=category).first()
        listing.save()
        category.entries -= 1
        category.save()
        # messages.success(request, f"Listing Closed!")
        return redirect('showlisting', id=listing.id)
    else :
        return HttpResponse("Not post")