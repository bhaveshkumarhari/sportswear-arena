# Generated by Django 3.0.5 on 2020-06-13 11:14

from django.db import migrations, models
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_auto_20200613_0935'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='variation',
            managers=[
                ('object', django.db.models.manager.Manager()),
            ],
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='size',
        ),
        migrations.AddField(
            model_name='orderitem',
            name='variations',
            field=models.ManyToManyField(blank=True, null=True, to='core.Variation'),
        ),
    ]