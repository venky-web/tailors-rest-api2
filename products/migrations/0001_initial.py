# Generated by Django 4.0 on 2022-01-16 03:44

from django.db import migrations, models
import django.db.models.deletion
import products.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0008_remove_business_owner_remove_user_business_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(blank=True, null=True)),
                ('updated_on', models.DateTimeField(blank=True, null=True)),
                ('created_by', models.CharField(blank=True, max_length=255, null=True)),
                ('updated_by', models.CharField(blank=True, max_length=255, null=True)),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Name')),
                ('description', models.TextField(blank=True, default='', max_length=500)),
                ('image', models.ImageField(null=True, upload_to=products.models.image_file_path)),
                ('category', models.CharField(default='', max_length=255)),
                ('units_available', models.IntegerField(default=1)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('product_code', models.CharField(max_length=255, unique=True)),
                ('is_service', models.BooleanField(default=False)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_available', models.BooleanField(default=True)),
                ('seller', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='product', to='account.user')),
            ],
            options={
                'db_table': 't_product',
                'ordering': ('-updated_on',),
            },
        ),
        migrations.CreateModel(
            name='ProductDesignImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(blank=True, null=True)),
                ('updated_on', models.DateTimeField(blank=True, null=True)),
                ('created_by', models.CharField(blank=True, max_length=255, null=True)),
                ('updated_by', models.CharField(blank=True, max_length=255, null=True)),
                ('image', models.ImageField(upload_to=products.models.image_file_path)),
                ('image_code', models.CharField(blank=True, default='', max_length=50)),
                ('is_main_image', models.BooleanField(default=False)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_images', related_query_name='product_image', to='products.product')),
            ],
            options={
                'db_table': 't_product_design_image',
                'ordering': ('-updated_on',),
            },
        ),
    ]
