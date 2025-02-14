import django

django.setup()

import os
import re
import time

import praw
import sefaria.system.database as database
from sefaria.model import *
from sefaria.system.exceptions import InputError

reddit = praw.Reddit(
    client_id=os.environ.get('REDDIT_CLIENT_ID'),
    client_secret=os.environ.get('REDDIT_CLIENT_SECRET'),
    password=os.environ.get('REDDIT_PASSWORD'),
    user_agent=os.environ.get('REDDIT_USER_AGENT'),
    username=os.environ.get('REDDIT_USERNAME'),
    )

version_en = "The Holy Scriptures: A New Translation (JPS 1917)"
version_he = "Tanach with Nikkud"

def render_refs(refs):
    response = ""
    for oref in refs:
        if(oref.is_empty()):
            continue
        text = ""
        for he,en in list(zip(oref.text('he').ja(True).flatten_to_array(), oref.text('en').ja(True).flatten_to_array())):
            if he != "":
                text += he.strip() + "\n\n"
            if en != "":
                text += ">" + en.strip() + "\n\n"
        if(len(text) > 2000):
            response += f'See [{oref.orig_tref}](https://www.sefaria.org/{oref.url()}) on Sefaria.\n\n'
        else:
            response += f'[{oref.orig_tref}](https://www.sefaria.org/{oref.url()})\n\n'
            response += text
    return response

def process_comment(comment):
    print(comment.author.name + ": " + comment.body)
    print('searching for text refs')
    start = time.perf_counter()

    # split comment up
    lines = comment.body.split('\n')
    refs = []
    for line in lines:
        refs.extend(library.get_refs_in_string(line, "en", True))
    end = time.perf_counter()
    print(f"search took {end - start:0.4f} seconds")
    #remove duplicates
    refs = [*set(refs)]
    refs = sorted(refs, key=lambda x: x.normal())
    if len(refs) > 0:
        print("The following refs were found:")
        print(refs)
    else:
        print("No refs found.")
        return
    response = "*Dedicated to Dvora bat Jacot of blessed memory.* 🕯️\n\n"
    result = render_refs(refs)
    if(len(result) == 0):
        return
    response += result
    print(response)
    # TODO validate that the response is under 10,000 chars.
    comment.reply(response)