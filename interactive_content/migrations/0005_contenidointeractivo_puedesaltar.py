# Generated by Django 2.2.4 on 2020-03-25 01:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interactive_content', '0004_auto_20191027_2050'),
    ]

    operations = [
        migrations.AddField(
            model_name='contenidointeractivo',
            name='puedeSaltar',
            field=models.BooleanField(default=False),
        ),
    ]