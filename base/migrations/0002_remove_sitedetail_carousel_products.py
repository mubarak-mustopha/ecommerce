# Generated by Django 4.0.10 on 2024-10-22 00:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sitedetail',
            name='carousel_products',
        ),
    ]
