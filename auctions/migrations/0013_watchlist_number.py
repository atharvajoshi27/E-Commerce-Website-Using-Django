# Generated by Django 3.0.9 on 2020-08-15 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0012_food_place_restaurant'),
    ]

    operations = [
        migrations.AddField(
            model_name='watchlist',
            name='number',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
