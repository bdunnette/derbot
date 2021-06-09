# Generated by Django 3.2.4 on 2021-06-09 20:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('names', '0005_derbyname_toot_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='ColorScheme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('hex', models.CharField(max_length=20, unique=True)),
                ('r', models.IntegerField(default=0)),
                ('g', models.IntegerField(default=0)),
                ('b', models.IntegerField(default=0)),
                ('pair_with', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='names.colorscheme')),
            ],
        ),
    ]
