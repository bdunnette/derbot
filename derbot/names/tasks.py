import random
import string
# import requests
from django.conf import settings
from django.utils import timezone
from huey.contrib.djhuey import db_task, task
from inscriptis import get_text
from bs4 import BeautifulSoup
import requests


from derbot.names.models import DerbyName
from django.db.models import Q


@db_task()
def generate_names(batch_size=10, default_temp=settings.DEFAULT_TEMP, random_temps=settings.USE_RANDOM_TEMPS,
                   min_temp=settings.MIN_TEMP, max_temp=settings.MAX_TEMP):
    from textgenrnn import textgenrnn
    model_path = settings.BASE_DIR.joinpath('derbot', 'model')
    textgen = textgenrnn(weights_path=model_path.joinpath('{}_weights.hdf5'.format(settings.MODEL_NAME)),
                         vocab_path=model_path.joinpath(
                             '{}_vocab.json'.format(settings.MODEL_NAME)),
                         config_path=model_path.joinpath('{}_config.json'.format(settings.MODEL_NAME)))

    if random_temps:
        temperature = [round(random.uniform(min_temp, max_temp), 1)
                       for i in range(batch_size)]
    else:
        temperature = [default_temp]

    new_names = textgen.generate(
        batch_size, temperature=temperature, return_as_list=True)

    new_name_objs = [DerbyName(name=name, generated=timezone.now(),
                               temperature=temperature[idx]) for idx, name in enumerate(new_names)]

    DerbyName.objects.bulk_create(new_name_objs, ignore_conflicts=True)

    return("Generated {0} names: {1}".format(len(new_name_objs), new_name_objs))


@db_task()
def fetch_toots(mastodon=settings.MASTO):
    account_id = mastodon.account_verify_credentials()['id']
    print("Downloading statuses for account {0}...".format(account_id))
    statuses = mastodon.account_statuses(account_id, exclude_replies=True)
    while statuses:
        print(statuses)
        print(dir(statuses))
        new_name_objs = [DerbyName(name=get_text(s.content).strip(
        ), tooted=s.created_at, reblogs_count=s.reblogs_count, favourites_count=s.favourites_count) for s in statuses]
        DerbyName.objects.bulk_create(new_name_objs, ignore_conflicts=True)
        statuses = mastodon.fetch_next(statuses)


@db_task()
def toot_name(name_id=None, mastodon=settings.MASTO):
    if name_id:
        name = DerbyName.objects.get(pk=name_id)
    else:
        name = DerbyName.objects.filter(
            Q(registered=False) & Q(tooted=None) & Q(cleared=True)
        ).order_by("?").first()
    if name:
        print("Tooting name '{0}'...".format(name))
        toot = mastodon.status_post(name)
        print("  Tooted at {0}".format(toot.created_at))
        name.tooted = toot.created_at
        name.save()


@db_task()
def fetch_names_twoevils(session=settings.SESSION, timeout=settings.REQUEST_TIMEOUT):
    url = "https://www.twoevils.org/rollergirls/"
    print("Downloading names from %s" % url)
    r = session.get(url, timeout=timeout)
    soup = BeautifulSoup(r.text, "lxml")
    rows = soup.find_all('tr', {'class': ['trc1', 'trc2']})
    names = [row.find('td').get_text() for row in rows]
    new_name_objs = [DerbyName(name=n, registered=True)
                     for n in names if len(n) > 1]
    DerbyName.objects.bulk_create(new_name_objs, ignore_conflicts=True)


@db_task()
def fetch_names_drc(session=settings.SESSION, timeout=settings.REQUEST_TIMEOUT):
    url = "http://www.derbyrollcall.com/everyone"
    print("Downloading names from %s" % url)
    r = session.get(url, timeout=timeout)
    soup = BeautifulSoup(r.text, "lxml")
    rows = soup.find_all('td', {'class': 'name'})
    names = [td.get_text() for td in rows]
    new_name_objs = [DerbyName(name=n, registered=True)
                     for n in names if len(n) > 1]
    DerbyName.objects.bulk_create(new_name_objs, ignore_conflicts=True)


@db_task()
def fetch_names_wftda(session=settings.SESSION, timeout=settings.REQUEST_TIMEOUT):
    url = 'https://resources.wftda.org/officiating/roller-derby-certification-program-for-officials/roster-of-certified-officials/'
    print("Downloading names from {0}".format(url))
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    r = session.get(url, timeout=timeout)
    soup = BeautifulSoup(r.text, "lxml")
    rows = soup.find_all('h5')
    names = [r.find('a').get_text() for r in rows]
    new_name_objs = [DerbyName(name=n, registered=True)
                     for n in names if len(n) > 1]
    DerbyName.objects.bulk_create(new_name_objs, ignore_conflicts=True)


@task()
def fetch_names_rdr(initial_letters=string.ascii_uppercase+string.digits+string.punctuation):
    for letter in initial_letters:
        fetch_names_rdr_letter(letter)


@db_task()
def fetch_names_rdr_letter(letter=None, session=settings.SESSION, timeout=settings.REQUEST_TIMEOUT):
    if letter:
        try:
            names = []
            url = "https://rollerderbyroster.com/view-names/?ini={0}".format(
                letter)
            print("Downloading names from {0}".format(url))
            r = session.get(url, timeout=timeout)
            soup = BeautifulSoup(r.text, "lxml")
            rows = soup.find_all('ul')
            # Use only last unordered list - this is where names are!
            for idx, li in enumerate(rows[-1]):
                # Name should be the text of the link within the list item
                name = li.find('a').get_text()
                names.append(name)
            new_name_objs = [DerbyName(name=n, registered=True)
                             for n in names if len(n) > 1]
            DerbyName.objects.bulk_create(new_name_objs, ignore_conflicts=True)
        except requests.Timeout:
            print("  Timeout reading from {0}".format(url))
            pass
    else:
        print("Need initial letter!")
        return False
