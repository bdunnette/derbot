# Generated by Django 3.2.3 on 2021-05-27 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('names', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='derbyname',
            name='temperature',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
