import django

django.setup()

import os
import re
import time
import praw
import sefaria.system.database as database
from sefaria.model import *
from sefaria.system.exceptions import InputError
# from sefaria.utils.calendars import daf_yomi, parashat_hashavua_and_haftara
from sefaria.utils.calendars import daf_yomi
# from datetime import datetime, timedelta
from datetime import datetime

def main():
    reddit = praw.Reddit(
        client_id=os.environ.get('REDDIT_CLIENT_ID'),
        client_secret=os.environ.get('REDDIT_CLIENT_SECRET'),
        password=os.environ.get('REDDIT_PASSWORD'),
        user_agent=os.environ.get('REDDIT_USER_AGENT'),
        username=os.environ.get('REDDIT_USERNAME'),
        )

    # data = parashat_hashavua_and_haftara(datetime.now(),True)
    now = datetime.now()
    data = daf_yomi(now)
    print(data)
    print(data[0]["ref"])

    # version_en = "The Holy Scriptures: A New Translation (JPS 1917)"
    # version_he = "Tanach with Nikkud"

    title = f'{data[0]["title"]["en"]} for {now.strftime("%b %d, %Y")}: {data[0]["displayValue"]["en"]}'
    print(title)
    # content = f'*{data[0]["description"]["en"]}*\n\n'
    content = "*Dedicated to Dvora bat Jacot of blessed memory.* 🕯️\n\n"

    # content += f'As translated in **{version_en}**\n\n'
    sefaria_host = "https://www.sefaria.org/"

    oref = Ref(data[0]["ref"])
    range_list = oref.range_list()
    book = Ref(range_list[0].book)
    chapter, _ = range_list[0].in_terms_of(book)
    is_first = True
    for ref in range_list:
        c, v = ref.in_terms_of(book)
        buf = ''
        if(is_first):
            is_first = False
            buf += f'**[{ref.book} {c}:{v}]({sefaria_host}{ref.url()})**\n'
        elif(c != chapter):
            buf += f'**[{ref.book} {c}:{v}]({sefaria_host}{ref.url()})**\n'
            chapter = c
        else:
            buf += f'**[{v}]({sefaria_host}{ref.url()})**\n'
        he = ref.text("he").ja(True).flatten_to_string().strip()
        en = ref.text("en").ja(True).flatten_to_string().strip()
        buf += f'{he}\n\n'
        buf += f'>{en}\n\n'

        see_rest = f'See the rest on [Sefaria]({sefaria_host}{ref.url()}).'
        if(len(buf) + len(content) > 40000 - len(see_rest)):
            # see the rest on sefaria
            content += see_rest
            break
        else:
            content += buf

    reddit.subreddit("TorahBot").submit(title, selftext=content)
    print(content)
    print(f'{len(content)} characters written.')

if __name__ == "__main__":
    main()

