# Generated by Django 4.0 on 2022-01-31 15:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0008_remove_business_owner_remove_user_business_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='business',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.business'),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_role',
            field=models.CharField(choices=[('normal_user', 'Normal user'), ('business_admin', 'Business admin'), ('business_staff', 'Business staff'), ('admin', 'Admin')], default='normal_user', max_length=50, verbose_name='User role'),
        ),
    ]
