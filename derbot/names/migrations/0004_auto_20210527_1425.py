# Generated by Django 3.2.3 on 2021-05-27 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('names', '0003_auto_20210527_1419'),
    ]

    operations = [
        migrations.AddField(
            model_name='derbyname',
            name='favourites_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='derbyname',
            name='reblogs_count',
            field=models.IntegerField(default=0),
        ),
    ]
