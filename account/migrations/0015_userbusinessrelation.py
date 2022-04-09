# Generated by Django 4.0 on 2022-04-06 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0014_alter_userprofile_phone'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserBusinessRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=100)),
                ('business_id', models.CharField(max_length=100)),
                ('request_status', models.CharField(default='pending', max_length=255)),
                ('request_date', models.DateTimeField()),
                ('request_expiry_date', models.DateTimeField()),
                ('updated_date', models.DateTimeField()),
            ],
            options={
                'db_table': 't_user_business_relation',
                'ordering': ('-request_date',),
            },
        ),
    ]