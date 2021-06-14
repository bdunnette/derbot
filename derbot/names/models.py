from django.db import models
import random
import humanize


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
    jersey = models.ImageField(upload_to="jerseys/", null=True, blank=True)
    fg_color = models.ForeignKey(
        "ColorScheme",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="jersey_fg",
    )
    bg_color = models.ForeignKey(
        "ColorScheme",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="jersey_bg",
    )

    def __str__(self):
        return self.name

    def get_number(self):
        if not self.number:
            jersey_number = str(random.uniform(1, 9999))[
                random.randint(0, 3) : random.randint(5, 7)
            ].strip(".")
            to_humanize = bool(random.getrandbits(1))
            if to_humanize == True:
                jersey_number = humanize.fractional(jersey_number)
            self.number = jersey_number
        return self.number

    def get_jersey_colors(self):
        if self.fg_color is None or self.bg_color is None:
            fg_color = ColorScheme.objects.order_by("?").first()
            bg_color = fg_color.pair_with
            self.fg_color = fg_color
            self.bg_color = bg_color
            self.save()
        return (self.fg_color, self.bg_color)


class ColorScheme(models.Model):
    name = models.CharField(max_length=255)
    hex = models.CharField(max_length=20, unique=True)
    r = models.IntegerField(default=0)
    g = models.IntegerField(default=0)
    b = models.IntegerField(default=0)
    pair_with = models.ForeignKey("self", null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

    def rgb(self):
        return (self.r, self.g, self.b)
