# Generated by Django 4.1.2 on 2022-10-19 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_basket'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basket',
            name='number_of_items',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
