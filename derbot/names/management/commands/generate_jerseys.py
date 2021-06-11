from django.core.management.base import BaseCommand, CommandError
from derbot.names.tasks import generate_jerseys

class Command(BaseCommand):
    help = 'Generates jerseys for names'

    def add_arguments(self, parser):
        parser.add_argument('name_ids', nargs='*', type=int, default=None)

    def handle(self, *args, **options):
        generate_jerseys(name_ids=options['name_ids'])