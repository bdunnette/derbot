from django.db import models


class DerbyName(models.Model):
    name = models.CharField(max_length=255, unique=True)
    number = models.CharField(max_length=64, null=True, blank=True)
    registered = models.BooleanField(default=False)
    cleared = models.BooleanField(default=False)
    generated = models.DateTimeField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    tooted = models.DateTimeField(null=True, blank=True)
    toot_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    reblogs_count = models.IntegerField(default=0)
    favourites_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name
        

class ColorScheme(models.Model):
    name = models.CharField(max_length=255)
    hex = models.CharField(max_length=20, unique=True)
    r = models.IntegerField(default=0)
    g = models.IntegerField(default=0)
    b = models.IntegerField(default=0)
    pair_with = models.ForeignKey('self', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

    def rgb(self):
        return (self.r, self.g, self.b)