# Generated by Django 4.1.7 on 2023-02-24 15:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0014_alter_listing_winner'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listing',
            name='winner',
        ),
    ]