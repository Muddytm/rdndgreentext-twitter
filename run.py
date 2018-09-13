import config
import praw
import tweepy

# Configure Twitter authentication
auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_token, config.access_token_secret)
api = tweepy.API(auth)
#api.update_status("Hello world! (Again.)")

# Configure Reddit authentication
reddit = praw.Reddit(user_agent="For use with Twitter account: dndgreentext")
reddit.login(config.user, config.password, disable_warning=True)

while True:
    sub = reddit.subreddit(config.subreddit)
    for submission in sub.hot(limit=100):
        print (submission.title)
    break
