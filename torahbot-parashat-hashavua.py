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
from sefaria.utils.calendars import parashat_hashavua_and_haftara
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

    data = parashat_hashavua_and_haftara(datetime.now(),True)
    # version_en = "The Holy Scriptures: A New Translation (JPS 1917)"
    version_en = "The Contemporary Torah, Jewish Publication Society, 2006"
    version_he = "Tanach with Nikkud"

    title = f'Weekly Torah Portion: {data[0]["displayValue"]["en"]}'
    content = f'*{data[0]["description"]["en"]}*\n\n'

    content += f'As translated in **{version_en}**\n\n'

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
            buf += f'**[{ref.book} {c}:{v}]({ref.url()})**\n'
        elif(c != chapter):
            buf += f'**[{ref.book} {c}:{v}]({ref.url()})**\n'
            chapter = c
        else:
            buf += f'**[{v}]({ref.url()})**\n'
        he = ref.text("he", version_he).ja(True).flatten_to_string().strip()
        en = ref.text("en", version_en).ja(True).flatten_to_string().strip()
        # buf += f'{he}\n\n'
        buf += f'>{en}\n\n'

        see_rest = f'See the rest on [Sefaria]({ref.url()}).'
        if(len(buf) + len(content) > 40000 - len(see_rest)):
            # see the rest on sefaria
            content += see_rest
            break
        else:
            content += buf

    # print(title)
    # print(content)
    reddit.subreddit(os.environ.get('REDDIT_SUB')).submit(title, selftext=content)
    print(len(content))

    # subreddit = reddit.subreddit("judaism")
    # subreddit = reddit.subreddit("torahbot_test")
    # for comment in subreddit.stream.comments(skip_existing=True):
    #     # discard if it belongs to me
    #     if comment.author.name == "TorahBot":
    #         print("discarding comment from me")
    #         continue
    #     else:
    #         job = queue.enqueue(torahbotworker.process_comment, comment)
    #         print(job)

if __name__ == "__main__":
    main()

