# Generated by Django 4.0.10 on 2024-10-22 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_remove_sitedetail_carousel_products'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitedetail',
            name='banner_img1',
            field=models.ImageField(default='', upload_to='assets/'),
        ),
        migrations.AddField(
            model_name='sitedetail',
            name='banner_img2',
            field=models.ImageField(default='', upload_to='assets/'),
        ),
        migrations.AddField(
            model_name='sitedetail',
            name='banner_img3',
            field=models.ImageField(default='', upload_to='assets/'),
        ),
    ]