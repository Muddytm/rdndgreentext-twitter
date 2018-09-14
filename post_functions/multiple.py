"""Functions for multiple image stuff (imgur albums, mainly)."""

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


def multiple_images(submission, data):
    """Process for posting multiple images (imgur albums supported)."""
    # Initial configuration
    album_id = submission.url.split("/a/")[1]
    file_num = 0
    filenames = []
    media = []

    # No more than 4 images allowed.
    if len(imgur.get_album_images(album_id)) > 4:
        return False

    # For every image in album, build it and media_upload it.
    for image in imgur.get_album_images(album_id):
        # Get image extension and construct filename
        ext = image.link[-3:]
        filename = "images/image{}.{}".format(str(file_num), ext)

        # Download and build image
        request = requests.get(image.link, stream=True)
        if request.status_code == 200:
            with open(filename, "wb") as image:
                for chunk in request:
                    image.write(chunk)
        else:
            return False

        # Upload and add to media list. Also add filename to filenames list.
        pic = api.media_upload(filename)
        media.append(pic.media_id)
        filenames.append(filename)

        file_num += 1

    # Build title
    if len(submission.title) > 160:
        title = submission.title[:160] + "..."
    else:
        title = submission.title

    # Build and post tweet
    tweet = "{} - [posted by /u/{}]".format(title, submission.author.name)

    api.update_status(status=tweet, media_ids=media)

    # Clean up and add post id to posted.json
    for pic in filenames:
        os.unlink(pic)
    data["ids"].append(submission.id)
    with open("posted.json", "w") as f:
        json.dump(data, f)

    return True
