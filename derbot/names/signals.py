from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
import random
import fractions
import humanize

from derbot.names.tasks import generate_jersey
from derbot.names.models import DerbyName, ColorScheme


@receiver(pre_save, sender=DerbyName)
def generate_number(sender, instance, **kwargs):
    if instance.cleared and not instance.number:
        jersey_number = str(random.uniform(1, 9999))[
            random.randint(0, 3) : random.randint(5, 7)
        ].strip(".")
        to_humanize = bool(random.getrandbits(1))
        if to_humanize == True:
            jersey_number = humanize.fractional(jersey_number).replace("/", "⁄")
        instance.number = jersey_number


@receiver(pre_save, sender=DerbyName)
def generate_number(sender, instance, **kwargs):
    if instance.cleared and not instance.fg_color:
        fg_color = ColorScheme.objects.order_by("?").first()
        bg_color = fg_color.pair_with
        print(fg_color, bg_color)
        instance.fg_color = fg_color
        instance.bg_color = bg_color


@receiver(post_save, sender=DerbyName)
def generate_number(sender, instance, **kwargs):
    if instance.cleared and not instance.tooted and not instance.jersey:
        generate_jersey(name_id=instance.id)

