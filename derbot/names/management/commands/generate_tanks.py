from django.core.management.base import BaseCommand, CommandError
from derbot.names.tasks import generate_tanks

class Command(BaseCommand):
    help = 'Generates "tank" jersey(s) for name(s)'

    def add_arguments(self, parser):
        parser.add_argument('name_ids', nargs='*', type=int, default=None)

    def handle(self, *args, **options):
        generate_tanks(name_ids=options['name_ids'])