# Generated by Django 3.0.5 on 2020-07-23 16:23

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0044_admin'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Admin',
            new_name='AllUserProfiles',
        ),
    ]
