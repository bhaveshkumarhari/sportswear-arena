# Generated by Django 3.0.5 on 2020-04-12 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='image',
            field=models.ImageField(default=21, upload_to=''),
            preserve_default=False,
        ),
    ]