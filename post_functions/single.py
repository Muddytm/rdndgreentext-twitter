"""Functions for single image stuff."""

import config
from imgurpython import ImgurClient
import json
import os
import requests
import tweepy

# Configure Twitter authentication
auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_token, config.access_token_secret)
api = tweepy.API(auth)

# Configure Imgur authentication
imgur = ImgurClient(config.imgur_id, config.imgur_secret)


def single_image(submission, data):
    """Process for posting a single image."""
    # Figure out file name
    ext = submission.url[-3:]
    filename = "images/image.{}".format(ext)

    # Fetch image and build it
    request = requests.get(submission.url, stream=True)
    if request.status_code == 200:
        with open(filename, "wb") as image:
            for chunk in request:
                image.write(chunk)
    else:
        return False

    # Build title
    if len(submission.title) > 160:
        title = submission.title[:160] + "..."
    else:
        title = submission.title

    # Build and post tweet
    tweet = "{} (https://redd.it/{})".format(title, submission.author.id)
    api.update_with_media(filename, tweet)

    # Clean up and add post id to posted.json
    os.remove(filename)
    data["ids"].append(submission.id)
    with open("posted.json", "w") as f:
        json.dump(data, f)

    return True
