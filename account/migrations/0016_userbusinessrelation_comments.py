# Generated by Django 4.0 on 2022-04-06 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0015_userbusinessrelation'),
    ]

    operations = [
        migrations.AddField(
            model_name='userbusinessrelation',
            name='comments',
            field=models.TextField(blank=True, null=True),
        ),
    ]