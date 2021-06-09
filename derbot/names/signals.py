from django.db.models.signals import pre_save
from django.dispatch import receiver
import random
import fractions
import humanize

# from derbot.names.tasks import generate_number
from derbot.names.models import DerbyName


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
