from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.files.uploadedfile import SimpleUploadedFile

from django.core.files import File
from urllib.request import urlopen
from urllib.parse import urlparse
from tempfile import NamedTemporaryFile
import os
import urllib
from PIL import Image
from commerce.settings import BASE_DIR

UPLOAD_TO = "images/"

# def upload_location(instance, filename):
#     filebase, extension = filename.split('.')
#     return f'images/image_{instance.id}.{extension}'

class User(AbstractUser):
    id = models.AutoField(primary_key=True)

class Category(models.Model):
    category = models.CharField(max_length=20)
    entries = models.PositiveIntegerField(default=0)


class Listing(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    description = models.TextField()
    starting_bid = models.PositiveIntegerField()
    category = models.CharField(max_length=20, null=True, blank=True)
    image_file = models.ImageField(upload_to=UPLOAD_TO, null=True, blank=True)
    # UPLOAD_TO is a global variable defined
    image_url = models.URLField(null=True, blank=True)
    number_of_bids = models.PositiveIntegerField(default=0)
    max_bid = models.PositiveIntegerField(default=0)
    bid_owner_id = models.PositiveIntegerField(null=True)
    ncomments = models.PositiveIntegerField(default=0)
    time = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    category_belongs = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)

    def get_remote_image(self):
        if self.image_url and not self.image_file:
            result = request.urlretrieve(self.image_url)
            self.image_file.save(
                    os.path.basename(self.image_url),
                    File(open(result[0], 'rb'))
                    )
            self.save()

    def save(self, *args, **kwargs):
        # if self.image_url and not self.image_file:
        #     self.get_remote_image()
        super(Listing, self).save(*args, **kwargs)
        

        if self.image_url and not self.image_file:
            # Solution 1
            # img_url = self.image_url
            # basename = urlparse(img_url).path.split('/')[-1]
            # tmpfile, _ = urllib.request.urlretrieve(img_url)

            # new_image = models.ImageField()
            # new_image.attribute_a = True
            # new_image.attribute_b = 'False'
            # new_image.file = SimpleUploadedFile(basename, open(tmpfile, "rb").read())
            # # self.image_file = new_image
            # self.image_file.save(f"image_{self.id}", File(new_image))
            # Solution 1 ends here

            # Solution 2 (If nothing worked)
            # img_temp = NamedTemporaryFile(delete=True)
            # img_temp.write(urlopen(self.image_url).read())
            # # im = Image.open(img_temp)
            # # resized_img = im.resize((200, 200))
            # # resized_img.save(f'image_{self.id}')
            # img_temp.flush()
            # self.image_file.save(f"image_{self.id}", File(img_temp))
            # Solution 2 ends here

            # Solution 3
            # name = urlparse(img_url).path.split('/')[-1]
            img_url = self.image_url
            name = f"image_{self.id}"
            content = urllib.request.urlretrieve(img_url)

            # See also: http://docs.djangoproject.com/en/dev/ref/files/file/
            self.image_file.save(name, File(open(content[0], 'rb')), save=True)
            # Solution 3 ends here
        if self.image_file and not self.image_url:
            filename = self.image_file.name
            _, extension = filename.split('.')
            new_name = f"{UPLOAD_TO}image_{self.id}.{extension}"
            location = r"{BASE_DIR}/media/".format(BASE_DIR=BASE_DIR)
            os.rename(r"{location}/{filename}".format(location=location,filename=filename), r"{location}/{new_name}".format(location=location, new_name=new_name))
            self.image_file.name = new_name
            print("Path = ", self.image_file.path)
            print("url = ", self.image_file.url)
            print("filename = ", self.image_file.name)
        super(Listing, self).save(*args, **kwargs)

        # if self.image_file:
        #     img = Image.open(self.image_file.path) # Open image using self
        #     new_img = (300, 300)
        #     img.thumbnail(new_img)
        #     img.save(self.image_file.path)

class Bids(models.Model):
    price = models.PositiveIntegerField()
    maker = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)


class Watchlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Listing)
    number = models.PositiveIntegerField(default=0)

class Comment(models.Model):
    comment = models.CharField(max_length=200)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)

class Place(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=80)

    def __str__(self):
        return "%s the place" % self.name

class Food(models.Model):
    name = models.CharField(max_length=20)

class Restaurant(models.Model):
    place = models.OneToOneField(
        Place,
        on_delete=models.CASCADE
    )
    foods = models.ManyToManyField(Food)