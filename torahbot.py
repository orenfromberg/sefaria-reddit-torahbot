import torahbotworker
import praw
import os

from redis import Redis
from rq import Queue

queue = Queue(connection=Redis(host=os.environ.get('REDIS_HOSTNAME')))


def main():
    username = os.environ.get('REDDIT_USERNAME')

    reddit = praw.Reddit(
        client_id=os.environ.get('REDDIT_CLIENT_ID'),
        client_secret=os.environ.get('REDDIT_CLIENT_SECRET'),
        password=os.environ.get('REDDIT_PASSWORD'),
        user_agent=os.environ.get('REDDIT_USER_AGENT'),
        username=username
    )

    subreddit = reddit.subreddit(os.environ.get('REDDIT_SUB'))
    for comment in subreddit.stream.comments(skip_existing=True):
        # discard if it belongs to me
        if comment.author.name == username:
            print("discarding comment from me")
            continue
        else:
            job = queue.enqueue(torahbotworker.process_comment, comment)
            print(job)


if __name__ == "__main__":
    main()
