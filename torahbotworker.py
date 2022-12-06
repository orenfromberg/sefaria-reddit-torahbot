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
    user_agent="TorahBot (by u/o_m_f_g)",
    username="TorahBot",
    )

version_en = "The Holy Scriptures: A New Translation (JPS 1917)"
version_he = "Tanach with Nikkud"

def render_refs(refs):
    response = ""
    for oref in refs:
        if(oref.is_empty()):
            continue
        en = oref.text('en').ja(True).flatten_to_string().strip()
        he = oref.text('he').ja(True).flatten_to_string().strip()
        response += "# " + oref.tref + "\n\n"
        if(len(en) > 1000): # if more than 1000 chars
            # post a link to sefaria for the reference
            response += f'See the whole text on sefaria.org: https://www.sefaria.org/{oref.url()}\n\n'
        else:
            if he != "":
                response += he + "\n\n"
            if en != "":
                response += ">" + en + "\n\n"
            response += "\n"
    return response

def process_comment(comment):
    print(comment.author.name + ": " + comment.body)
    print('searching for text refs')
    start = time.perf_counter()
    refs = library.get_refs_in_string(comment.body, "en", True)
    end = time.perf_counter()
    print(f"search took {end - start:0.4f} seconds")
    #remove duplicates
    refs = [*set(refs)]
    if len(refs) > 0:
        print("The following refs were found:")
        print(refs)
    else:
        print("No refs found.")
        return
    response = "*Dedicated to Dvora bat Jacot of blessed memory.*\n\n"
    result = render_refs(refs)
    if(len(result) == 0):
        return
    response += result
    print(response)
    # TODO validate that the response is under 10,000 chars.
    comment.reply(response)