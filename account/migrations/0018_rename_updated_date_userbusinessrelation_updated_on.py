# Generated by Django 4.0 on 2022-04-16 12:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0017_userbusinessrelation_updated_by'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userbusinessrelation',
            old_name='updated_date',
            new_name='updated_on',
        ),
    ]