# Generated by Django 5.0 on 2024-08-28 01:59

import django.contrib.auth.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('administration', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Elector',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('national_number', models.CharField(max_length=100, unique=True)),
                ('elector_token', models.CharField(max_length=100, unique=True)),
                ('country', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name': 'Elector',
                'verbose_name_plural': 'Electors',
            },
            bases=('users.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ElectoralList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('national_number', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('country', models.CharField(max_length=100)),
                ('election', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='electorlists', to='administration.election')),
            ],
            options={
                'verbose_name': 'ElectoralList',
                'verbose_name_plural': 'ElectoralLists',
            },
        ),
    ]
