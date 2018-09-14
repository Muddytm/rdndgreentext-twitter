"""Functions for handling raw text posts."""

import config
from PIL import Image, ImageDraw, ImageFont
from imgurpython import ImgurClient
import json
import os
import pprint
import requests
import tweepy

# Configure Twitter authentication
auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_token, config.access_token_secret)
api = tweepy.API(auth)


def clean(line):
    """Get rid of unicode bullcrap."""
    for char in line:
        if ord(char) > 127:
            line = line.replace(char, "")

    return line


def raw_text(submission, data):
    """Process for posting image(s) of raw text."""
    media = []
    filenames = []
    img_count = 0
    line_count = 0
    max_length = 400
    char_limit = 50
    line_limit = 48

    text = ""
    post_lines = clean(submission.selftext).splitlines()
    for line in post_lines:
        # No more than 4 images allowed
        if img_count > 3:
            return False

        og_line = line
        # If line is not blank
        if line:
            # Clean this up real quick.
            line = line.replace(">", "").replace("\\", "").strip()

            # If this line is too long, we just don't post at all.
            if len(line) > max_length:
                return False

            # Else, turn this line into a nicely-segmented block.
            substr = ""
            if len(line) > char_limit:
                word_length = 2 # Because of the "> " we'll put on later
                for word in line.split():
                    if (word_length + len(word)) <= char_limit:
                        substr += (word + " ")
                        word_length += (len(word) + 1)
                    elif len(word) > char_limit:
                        # Seriously? Don't even bother.
                        return False
                    else:
                        substr += ("\n" + word + " ")
                        line_count += 1
                        word_length = (len(word) + 1)
            else:
                substr = line

            text += "> {}\n\n".format(substr)
            line_count += 2

        # Next do a line count check to make sure there's room.
        if line_count >= line_limit:
            filename = "images/file{}.png".format(str(img_count))
            img = Image.new("RGB", (500, (17*line_count) + 20), color=(20, 29, 38))

            fnt = ImageFont.truetype(config.font, 17)
            d = ImageDraw.Draw(img)
            d.text((20, 20), text, font=fnt, fill=(164, 255, 211))
            img.save(filename)

            pic = api.media_upload(filename)
            media.append(pic.media_id)
            filenames.append(filename)

            img_count += 1
            line_count = 0
            text = ""

    # TODO: figure out a better solution than slapping this at the end...
    if line_count > 0:
        filename = "images/file{}.png".format(str(img_count))
        img = Image.new("RGB", (500, (17*line_count) + 20), color=(20, 29, 38))

        fnt = ImageFont.truetype(config.font, 17)
        d = ImageDraw.Draw(img)
        d.text((20, 20), text, font=fnt, fill=(164, 255, 211))
        img.save(filename)

        pic = api.media_upload(filename)
        media.append(pic.media_id)
        filenames.append(filename)

    # Build title
    if len(submission.title) > 160:
        title = submission.title[:160] + "..."
    else:
        title = submission.title

    # Build and post tweet
    tweet = clean("{} - [posted by /u/{}]".format(title, submission.author.name))
    api.update_status(status=tweet, media_ids=media)

    # Clean up and add post id to posted.json
    for pic in filenames:
        os.unlink(pic)
    data["ids"].append(submission.id)
    with open("posted.json", "w") as f:
        json.dump(data, f)

    return True
