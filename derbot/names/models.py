from django.db import models


class DerbyName(models.Model):
    name = models.CharField(max_length=255, unique=True)
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
