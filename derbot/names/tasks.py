import random
import string
import os
import logging

import requests
from bs4 import BeautifulSoup
from derbot.names.models import DerbyName, ColorScheme
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from django.core.files import File
from io import BytesIO
from PIL import Image, ImageOps, ImageDraw, ImageFont
from huey import crontab
from huey.contrib.djhuey import db_periodic_task, db_task, task
from inscriptis import get_text


def hex_to_rgb(hex):
    rgb = tuple(int(hex[i : i + 2], 16) for i in (0, 2, 4))
    return rgb


def text_wrap(text, font, max_width):
    # From https://fiveminutes.today/articles/putting-text-on-images-with-python-pil/
    lines = []
    # If the width of the text is smaller than image width
    # we don't need to split it, just add it to the lines array
    # and return
    if font.getsize(text)[0] <= max_width:
        lines.append(text)
    else:
        # split the line by spaces to get words
        words = text.split(" ")
        i = 0
        # append every word to a line while its width is shorter than image width
        while i < len(words):
            line = ""
            while i < len(words) and font.getsize(line + words[i])[0] <= max_width:
                line = line + words[i] + " "
                i += 1
            if not line:
                line = words[i]
                i += 1
            # when the line gets longer than the max width do not append the word,
            # add the line to the lines array
            lines.append(line.strip())
    return lines


@db_periodic_task(crontab(minute="20"))
def generate_names(
    batch_size=100,
    default_temp=settings.DEFAULT_TEMP,
    random_temps=settings.USE_RANDOM_TEMPS,
    min_temp=settings.MIN_TEMP,
    max_temp=settings.MAX_TEMP,
):
    from textgenrnn import textgenrnn

    model_path = settings.BASE_DIR.joinpath("derbot", "model")
    textgen = textgenrnn(
        weights_path=model_path.joinpath("{}_weights.hdf5".format(settings.MODEL_NAME)),
        vocab_path=model_path.joinpath("{}_vocab.json".format(settings.MODEL_NAME)),
        config_path=model_path.joinpath("{}_config.json".format(settings.MODEL_NAME)),
    )

    if random_temps:
        temperature = [
            round(random.uniform(min_temp, max_temp), 1) for i in range(batch_size)
        ]
    else:
        temperature = [default_temp]

    new_names = textgen.generate(
        batch_size, temperature=temperature, return_as_list=True
    )

    new_name_objs = [
        DerbyName(name=name, generated=timezone.now(), temperature=temperature[idx])
        for idx, name in enumerate(new_names)
    ]

    DerbyName.objects.bulk_create(new_name_objs, ignore_conflicts=True)

    return "Generated {0} names: {1}".format(len(new_name_objs), new_name_objs)


@db_periodic_task(crontab(hour="3", minute="0"))
def fetch_toots(mastodon=settings.MASTO):
    account_id = mastodon.account_verify_credentials()["id"]
    print("Downloading statuses for account {0}...".format(account_id))
    statuses = mastodon.account_statuses(account_id, exclude_replies=True)
    while statuses:
        # print(statuses)
        # print(dir(statuses))
        new_name_objs = [
            DerbyName(
                name=get_text(s.content).strip(),
                toot_id=s.id,
                tooted=s.created_at,
                reblogs_count=s.reblogs_count,
                favourites_count=s.favourites_count,
            )
            for s in statuses
        ]
        DerbyName.objects.bulk_create(new_name_objs, ignore_conflicts=True)
        statuses = mastodon.fetch_next(statuses)


@db_periodic_task(crontab(minute="1"))
def toot_name(
    name_id=None,
    mastodon=settings.MASTO,
    do_wait=settings.DO_WAIT,
    min_wait=settings.MIN_WAIT,
    max_wait=settings.MAX_WAIT,
):
    if name_id:
        name = DerbyName.objects.get(pk=name_id)
    else:
        name = (
            DerbyName.objects.filter(
                Q(registered=False) & Q(tooted=None) & Q(cleared=True)
            )
            .order_by("?")
            .first()
        )

    if name:
        if do_wait:
            delay = random.randint(min_wait, max_wait)
            print("Waiting {0} seconds before tooting {1}".format(delay, name))
            toot_name.schedule(
                kwargs={"name_id": name.pk, "do_wait": False}, delay=delay
            )
        else:
            print("Tooting name '{0}'...".format(name))
            if name.jersey == "":
                toot = mastodon.status_post(name)
            else:
                image_description = "{0}-colored shirt with '{1}'\
                        and the number {2} printed on it in {3} lettering.".format(
                    str(name.bg_color), str(name), name.number, str(name.fg_color)
                )
                logging.info(image_description)
                media = mastodon.media_post(
                    name.jersey, mime_type="image/jpeg", description=image_description
                )
                logging.debug(media)
                toot = mastodon.status_post(name, media_ids=media)
            print("  Tooted at {0}".format(toot.created_at))
            name.toot_id = toot.id
            name.tooted = toot.created_at
            name.save()
            return name
    else:
        print("No matching names found, exiting...")
        return False


@db_periodic_task(crontab(hour="3", minute="0"))
def fetch_names_twoevils(session=settings.SESSION, timeout=settings.REQUEST_TIMEOUT):
    url = "https://www.twoevils.org/rollergirls/"
    print("Downloading names from %s" % url)
    r = session.get(url, timeout=timeout)
    soup = BeautifulSoup(r.text, "lxml")
    rows = soup.find_all("tr", {"class": ["trc1", "trc2"]})
    names = [row.find("td").get_text() for row in rows]
    new_name_objs = [DerbyName(name=n, registered=True) for n in names if len(n) > 1]
    DerbyName.objects.bulk_create(new_name_objs, ignore_conflicts=True)


@db_periodic_task(crontab(hour="3", minute="0"))
def fetch_names_drc(session=settings.SESSION, timeout=settings.REQUEST_TIMEOUT):
    url = "http://www.derbyrollcall.com/everyone"
    print("Downloading names from %s" % url)
    r = session.get(url, timeout=timeout)
    soup = BeautifulSoup(r.text, "lxml")
    rows = soup.find_all("td", {"class": "name"})
    names = [td.get_text() for td in rows]
    new_name_objs = [DerbyName(name=n, registered=True) for n in names if len(n) > 1]
    DerbyName.objects.bulk_create(new_name_objs, ignore_conflicts=True)


@db_periodic_task(crontab(hour="3", minute="0"))
def fetch_names_wftda(session=settings.SESSION, timeout=settings.REQUEST_TIMEOUT):
    url = "https://resources.wftda.org/officiating/roller-derby-certification-program-for-officials/roster-of-certified-officials/"
    print("Downloading names from {0}".format(url))
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    r = session.get(url, timeout=timeout)
    soup = BeautifulSoup(r.text, "lxml")
    rows = soup.find_all("h5")
    names = [r.find("a").get_text() for r in rows]
    new_name_objs = [DerbyName(name=n, registered=True) for n in names if len(n) > 1]
    DerbyName.objects.bulk_create(new_name_objs, ignore_conflicts=True)


@db_periodic_task(crontab(hour="3", minute="0"))
def fetch_names_rdr(
    initial_letters=string.ascii_uppercase + string.digits + string.punctuation,
):
    for letter in initial_letters:
        fetch_names_rdr_letter(letter)


@db_task()
def fetch_names_rdr_letter(
    letter=None, session=settings.SESSION, timeout=settings.REQUEST_TIMEOUT
):
    if letter:
        try:
            names = []
            url = "https://rollerderbyroster.com/view-names/?ini={0}".format(letter)
            print("Downloading names from {0}".format(url))
            r = session.get(url, timeout=timeout)
            soup = BeautifulSoup(r.text, "lxml")
            rows = soup.find_all("ul")
            # Use only last unordered list - this is where names are!
            for idx, li in enumerate(rows[-1]):
                # Name should be the text of the link within the list item
                name = li.find("a").get_text()
                names.append(name)
            new_name_objs = [
                DerbyName(name=n, registered=True) for n in names if len(n) > 1
            ]
            DerbyName.objects.bulk_create(new_name_objs, ignore_conflicts=True)
        except requests.Timeout:
            print("  Timeout reading from {0}".format(url))
            pass
    else:
        print("Need initial letter!")
        return False


@db_periodic_task(crontab(hour="3", minute="0"))
def fetch_colors(mastodon=settings.MASTO, color_bot=settings.COLOR_BOT):
    account_id = mastodon.account_search(color_bot)[0]["id"]
    statuses = mastodon.account_statuses(account_id, exclude_replies=True)
    while statuses:
        for s in statuses:
            if s.favourites_count > 0:
                # Get first two items/lines from toot, since these contain colors
                status_colors = get_text(s.content).strip().splitlines()[:2]
                # Get last element of each line, containing color hex code
                color_codes = [
                    {
                        "hex": c.split()[-1].lstrip("#"),
                        "rgb": hex_to_rgb(c.split()[-1].lstrip("#")),
                        "name": " ".join(c.split()[:-1]).rstrip("#").strip(),
                    }
                    for c in status_colors
                ]
                color1 = color_codes[0]
                c1, created = ColorScheme.objects.update_or_create(
                    name=color1["name"],
                    hex=color1["hex"],
                    r=color1["rgb"][0],
                    g=color1["rgb"][1],
                    b=color1["rgb"][2],
                )
                color2 = color_codes[1]
                c2, created = ColorScheme.objects.update_or_create(
                    name=color2["name"],
                    hex=color2["hex"],
                    r=color2["rgb"][0],
                    g=color2["rgb"][1],
                    b=color2["rgb"][2],
                    pair_with=c1,
                )
                c1.pair_with = c2
                c1.save()
        statuses = mastodon.fetch_next(statuses)


@db_task()
def generate_jersey(name_id):
    name = DerbyName.objects.get(pk=name_id)
    im = Image.open(
        settings.BASE_DIR.joinpath("derbot", "names", "images", "t-shirt.jpg")
    )
    fg_color, bg_color = name.get_jersey_colors()
    number = name.get_number()
    im_gray = ImageOps.grayscale(im)
    im_color = ImageOps.colorize(im_gray, bg_color.rgb(), "white")
    draw = ImageDraw.Draw(im_color)
    font = random.choice(settings.FONTS)
    font_path = os.path.join(settings.FONT_DIR, font)
    fnt1 = ImageFont.truetype(font_path, size=settings.TEXT_FONT_SIZE)
    w, h = draw.textsize(name.name, font=fnt1)
    lines = text_wrap(name.name, fnt1, settings.MAX_TEXT_WIDTH)
    y = (im_color.height - h) * 0.2
    for line in lines:
        line_width, line_height = draw.textsize(line, font=fnt1)
        draw.text(
            ((im_color.width - line_width) / 2, y), line, fill=fg_color.rgb(), font=fnt1
        )
        y += line_height
    nfs = settings.NUMBER_FONT_SIZE
    fnt2 = ImageFont.truetype(font_path, size=nfs)
    w, h = draw.textsize(number, font=fnt2)
    while w > settings.MAX_NUMBER_WIDTH:
        nfs = nfs - 10
        fnt2 = ImageFont.truetype(font_path, size=nfs)
        w, h = draw.textsize(number, font=fnt2)
    draw.text(((im_color.width - w) / 2, y), number, fill=fg_color.rgb(), font=fnt2)
    blob = BytesIO()
    im_color.save(blob, "JPEG")
    name.jersey.save("{}.jpg".format(name.id), File(blob), save=True)
