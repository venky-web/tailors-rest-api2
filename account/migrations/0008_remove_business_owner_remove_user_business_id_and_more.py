# Generated by Django 4.0 on 2022-01-16 03:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0007_user_business_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='business',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='user',
            name='business_id',
        ),
        migrations.AddField(
            model_name='business',
            name='staff_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='business',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
