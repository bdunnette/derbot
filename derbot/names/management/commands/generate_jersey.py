from django.core.management.base import BaseCommand, CommandError
from derbot.names.tasks import generate_jersey

class Command(BaseCommand):
    help = 'Generates names from TextgenRNN model'

    def add_arguments(self, parser):
        parser.add_argument('name_id', nargs='?', type=int, default=None)

    def handle(self, *args, **options):
        generate_jersey(name_id=options['name_id'])