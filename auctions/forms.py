from django.forms import ModelForm, Textarea
from django import forms
from .models import User, Listing, Bids

class CreateListing(ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_bid', 'category', 'image_file', 'image_url', ]
        # widgets = {
        #     'description': Textarea(attrs={'cols': 80, 'rows': 20}),
        # }
    
class BidsForm(ModelForm):
    class Meta:
        model = Bids
        fields = ['price']