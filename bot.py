#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tweepy, time, itertools
# EXAMPLE_KEY
CONSUMER_KEY = 'EXAMPLE_KEY'
CONSUMER_SECRET = 'EXAMPLE_KEY'
ACCESS_KEY = 'EXAMPLE_KEY'
ACCESS_SECRET = 'EXAMPLE_KEY'
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)
ignored_accounts = ["pyconsk", "Fl4shpower"]
hashtag = "#pyconskba"
number_of_tweets = 1000


# Helper Function for result pagination
def paginate(iterable, page_size):
    while True:
        i1, i2 = itertools.tee(iterable)
        iterable, page = (itertools.islice(i1, page_size, None),
                          list(itertools.islice(i2, page_size)))
        if len(page) == 0:
            break
        yield page


# Users that I'm following
def existing_followings():
    existing_followings = set()
    followers = api.friends_ids()
    print("\nRequesting Existing Followings...\n")

    for page in paginate(followers, 100):
        results = api.lookup_users(user_ids=page)
        for result in results:
            # print(result.screen_name) # For Debugging
            existing_followings.add(result.screen_name)

        time.sleep(10)

    return existing_followings


# Users who following me
def existing_followers():
    existing_followers = set()
    followers = api.followers_ids()
    print("\nRequesting Existing Followers...\n")

    for page in paginate(followers, 100):
        results = api.lookup_users(user_ids=page)
        for result in results:
            # print(result.screen_name) # For Debugging
            existing_followers.add(result.screen_name)

        time.sleep(10)

    return existing_followers

# Find Users with tweets with searching hashtag
def users_with_tweets():
    users_with_tweets = set()
    print("\nRequesting Existing Tweets...\n")
    for user in tweepy.Cursor(api.search, q=hashtag).items(number_of_tweets):
        screen_name = user.user.screen_name
        # print(screen_name) # For Debugging
        if screen_name in ignored_accounts:
            pass
        else:
            users_with_tweets.add(screen_name)

    return users_with_tweets


# Make new following
def follow_user(users_to_follow):
    print("\nFollowing Users...\n")
    for user in users_to_follow:
        api.create_friendship(screen_name=user)
        print("OK Following User: ", str(user))
        time.sleep(10)


try:
    existing_followings = existing_followings()
    print("\nexisting_followings :", len(existing_followings), "\n", existing_followings)
    existing_followers = existing_followers()
    print("\nexisting_followers :", len(existing_followers), "\n", existing_followers)
    users_with_tweets = users_with_tweets()
    print("\nusers_with_tweets :", len(users_with_tweets), "\n", users_with_tweets)
    users_to_follow = (users_with_tweets - (existing_followers.union(existing_followings)))
    print("\nusers_to_follow :", len(users_to_follow), "\n", users_to_follow)
    follow_user(users_to_follow)
    print("\nDone...")

except tweepy.TweepError as e:
    e = eval(str(e))
    print(e[0]['message'], "| Code :", e[0]['code'])
