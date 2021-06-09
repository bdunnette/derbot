from django.core.management.base import BaseCommand, CommandError
from derbot.names.tasks import fetch_toots

class Command(BaseCommand):
    help = 'Generates names from TextgenRNN model'

    def handle(self, *args, **options):
        fetch_toots()