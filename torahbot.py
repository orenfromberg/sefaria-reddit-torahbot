import django
django.setup()

from sefaria.model import *
import sefaria.system.database as database

import praw
import os

# print(TextChunk.remove_html_and_make_presentable(Ref('Genesis 1:1-2').text('he').text))
# print(Ref('Genesis 1:1-2').text('he').text)


def main():
    reddit = praw.Reddit(
    client_id=os.environ.get('CLIENT_ID'),
    client_secret=os.environ.get('CLIENT_SECRET'),
    password=os.environ.get('PASSWORD'),
    user_agent="TorahBot (by u/o_m_f_g)",
    username="TorahBot",
    )

    subreddit = reddit.subreddit("judaism")
    for comment in subreddit.stream.comments(skip_existing=True):
        print(comment.body)

if __name__ == "__main__":
    main()