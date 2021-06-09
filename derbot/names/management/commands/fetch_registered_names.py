from django.core.management.base import BaseCommand, CommandError
from derbot.names.tasks import fetch_names_twoevils, fetch_names_drc, fetch_names_wftda, fetch_names_rdr


class Command(BaseCommand):
    help = 'Downloads names from online databases'

    def handle(self, *args, **options):
        fetch_names_wftda()
        fetch_names_twoevils()
        fetch_names_drc()
        fetch_names_rdr()
