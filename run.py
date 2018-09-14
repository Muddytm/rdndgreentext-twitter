import config
import json
import os
import pprint
import praw
import requests
import tweepy

# Configure Twitter authentication
auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_token, config.access_token_secret)
api = tweepy.API(auth)
#api.update_status("Hello world! (Again.)")

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

# Get json of posts already posted, so there are no repeats (unless reposts lol)
# ...but first check if the file exists, and if not, create it
if not os.path.isfile("posted.json"):
    data = {}
    data["ids"] = []
else:
    with open("posted.json") as f:
        data = json.load(f)


for submission in sub.hot(limit=100):
    if (int(submission.ups) > threshold and
            not submission.stickied and
            (submission.url.endswith(".jpg") or
            submission.url.endswith(".png")) and
            submission.id not in data["ids"]):
        ext = submission.url[-3:]
        filename = "image.{}".format(ext)

        request = requests.get(submission.url, stream=True)
        if request.status_code == 200:
            with open(filename, "wb") as image:
                for chunk in request:
                    image.write(chunk)

        if len(submission.title) > 160:
            title = submission.title[:160] + "..."
        else:
            title = submission.title
        api.update_with_media(filename,
                              status="\"{}\" - (posted by {})".format(title,
                                                                      submission.author.name))
        os.remove(filename)
        data["ids"].append(submission.id)
        with open("posted.json", "w") as f:
            json.dump(data, f)
        break
        #print (submission.url)
        #pprint.pprint(vars(submission))
        #break
