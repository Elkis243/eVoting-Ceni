# Generated by Django 5.0 on 2024-08-29 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]