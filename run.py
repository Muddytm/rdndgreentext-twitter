import config
import json
import os
from PIL import Image, ImageDraw, ImageFont
import post_functions as pf
import pprint
import praw

# Configure Reddit authentication
reddit = praw.Reddit(client_id=config.client_id,
                     client_secret=config.client_secret,
                     password=config.password,
                     user_agent="Script by @Muddytm",
                     username=config.username)

# Threshold for how many points a post needs before it is considered worthy
# to upload to the Twitter account
threshold = 100

# Get subreddit in question (dndgreentext)
sub = reddit.subreddit(config.subreddit)


def run():
    """The main process."""
    # Get json of posts already posted, so there are no repeats (unless reposts lol)
    # ...but first check if the file exists, and if not, create it
    if not os.path.isfile("posted.json"):
        data = {}
        data["ids"] = []
    else:
        with open("posted.json") as f:
            data = json.load(f)

    for submission in sub.hot(limit=100):
        break
        if int(submission.ups) > threshold and not submission.stickied:
            # Single image posts - works with reddit and imgur links
            if ((submission.url.endswith(".jpg") or
                    submission.url.endswith(".png")) and
                    submission.id not in data["ids"]):
                # Run single_image() and wait until next cron job.
                # If single_image() runs into an error, continue to next.
                if pf.single_image(submission, data):
                    return
                else:
                    continue
            # If the post is an imgur album
            elif "/a/" in submission.url:
                if pf.multiple_images(submission, data):
                    return
                else:
                    continue

    for submission in sub.top(limit=100):
        if int(submission.ups) > threshold and not submission.stickied:
            # Single image posts - works with reddit and imgur links
            if ((submission.url.endswith(".jpg") or
                    submission.url.endswith(".png")) and
                    submission.id not in data["ids"]):
                # Run single_image() and wait until next cron job.
                # If single_image() runs into an error, continue to next.
                if pf.single_image(submission, data):
                    return
                else:
                    continue
            # If the post is an imgur album
            elif "/a/" in submission.url and submission.id not in data["ids"]:
                if pf.multiple_images(submission, data):
                    return
                else:
                    continue
            elif submission.id not in data["ids"]:
                if pf.raw_text(submission, data):
                    return
                else:
                    continue


if __name__ == "__main__":
    run()
