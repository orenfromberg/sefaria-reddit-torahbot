import praw
import os

from redis import Redis
from rq import Queue

queue = Queue(connection=Redis(host=os.environ.get('REDIS_HOSTNAME')))
import torahbotworker

def main():
    reddit = praw.Reddit(
    client_id=os.environ.get('REDDIT_CLIENT_ID'),
    client_secret=os.environ.get('REDDIT_CLIENT_SECRET'),
    password=os.environ.get('REDDIT_PASSWORD'),
    user_agent="TorahBot (by u/o_m_f_g)",
    username="TorahBot",
    )

    # subreddit = reddit.subreddit("judaism")
    subreddit = reddit.subreddit("torahbot_test")
    for comment in subreddit.stream.comments(skip_existing=True):
        # discard if it belongs to me
        if comment.author.name == "TorahBot":
            print("discarding comment from me")
            continue
        else:
            job = queue.enqueue(torahbotworker.process_comment, comment)
            print(job)

if __name__ == "__main__":
    main()