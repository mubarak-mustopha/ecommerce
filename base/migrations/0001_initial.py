# Generated by Django 4.0.10 on 2024-10-17 11:36

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0003_alter_brand_slug_alter_category_slug_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteDetail',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(default='Zay Shop', max_length=150)),
                ('email', models.EmailField(default='mubaarock021@gmail.com', max_length=254)),
                ('address', models.CharField(default='123 Consectetur at ligula 10660', max_length=300)),
                ('phone', models.CharField(default='+2347014887266', max_length=150)),
                ('fb', models.URLField(default='https://facebook.com', max_length=300, verbose_name='Facebook')),
                ('tw', models.URLField(default='https://twitter.com', max_length=300, verbose_name='Twitter')),
                ('ig', models.URLField(default='https://instagram.com', max_length=300, verbose_name='Instagram')),
                ('li', models.URLField(default='https://linkedin.com', max_length=300, verbose_name='LinkedIn')),
                ('carousel_products', models.ManyToManyField(related_name='carousel_products', to='products.product')),
                ('cats_of_month', models.ManyToManyField(related_name='cats_of_month', to='products.category', verbose_name='Categories of The Month')),
                ('featured_products', models.ManyToManyField(related_name='featured_products', to='products.product')),
            ],
        ),
    ]