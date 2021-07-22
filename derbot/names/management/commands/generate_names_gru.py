from django.core.management.base import BaseCommand, CommandError
from derbot.names.tasks import generate_names_numbers


class Command(BaseCommand):
    help = "Generates names from TextgenRNN model"

    def add_arguments(self, parser):
        parser.add_argument("batch_size", nargs="?", type=int, default=2500)

    def handle(self, *args, **options):
        generate_names_numbers(batch_size=options["batch_size"])
