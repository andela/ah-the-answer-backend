# Generated by Django 2.1.7 on 2019-04-02 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0003_profile_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='user_bio',
            field=models.TextField(help_text='Write a brief description about yourself.'),
        ),
    ]
