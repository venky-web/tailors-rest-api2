# Generated by Django 4.0 on 2022-01-08 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_alter_userprofile_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='created_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='created_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
