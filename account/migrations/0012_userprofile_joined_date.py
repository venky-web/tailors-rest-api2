# Generated by Django 4.0 on 2022-03-19 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0011_alter_user_business'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='joined_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
