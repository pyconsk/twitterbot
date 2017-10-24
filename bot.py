#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tweepy, time, itertools

CONSUMER_KEY = 'EXAMPLE_KEY'
CONSUMER_SECRET = 'EXAMPLE_KEY'
ACCESS_KEY = 'EXAMPLE_KEY'
ACCESS_SECRET = 'EXAMPLE_KEY'
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)
ignored_accounts = ["pyconsk"]
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
def existing_followings(pagination, sleep):
    existing_followings = set()
    followers = api.friends_ids()
    print("\nRequesting Existing Followings...\n")

    for page in paginate(followers, pagination):
        results = api.lookup_users(user_ids=page)
        for result in results:
            # print(result.screen_name) # For Debugging
            existing_followings.add(result.screen_name)

        print("Requesting 100 followings")
        time.sleep(sleep)

    return existing_followings


# Users who following me
def existing_followers(pagination, sleep):
    existing_followers = set()
    followers = api.followers_ids()
    print("\nRequesting Existing Followers...\n")

    for page in paginate(followers, pagination):
        results = api.lookup_users(user_ids=page)
        for result in results:
            # print(result.screen_name) # For Debugging
            existing_followers.add(result.screen_name)
            
        print("Requesting 100 followers")
        time.sleep(sleep)

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
def follow_user(users_to_follow, sleep):
    print("\nFollowing Users...\n")
    for user in users_to_follow:
        try:
            api.create_friendship(screen_name=user)
            print("OK Following User: ", str(user))
        except:
            pass
        time.sleep(sleep)


# Make unfollowing
def unfollow_user(users_to_unfollow, sleep):
    print("\nUnfollowing Users...\n")
    for user in users_to_unfollow:
        api.destroy_friendship(screen_name=user)
        print("OK Unfollowing User: ", str(user))
        time.sleep(sleep)


# Send private message to followers
def send_private_message(existing_followers, sleep, pm):
    for user in existing_followers:
        api.send_direct_message(user, text=pm)
        time.sleep(sleep)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--action', type=str, required=True, choices=['follow', 'unfollow', 'follow_followers',
                                                                            'pm'],
                        help='Action - follow | unfollow | follow_followers | pm')
    parser.add_argument('-p', '--pagination', type=int, default=100, help='Listing pagination')
    parser.add_argument('-s', '--sleep', type=int, default=10, help='Sleep time for function')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('--pm', type=str, help='pm - message to followers')
    args = parser.parse_args()
    sleep = args.sleep
    action = args.action
    pagination = args.pagination
    pm = args.pm
    try:
        existing_followings = existing_followings(pagination, sleep)
        print("\nexisting_followings :", len(existing_followings), "\n", existing_followings)
        existing_followers = existing_followers(pagination, sleep)
        print("\nexisting_followers :", len(existing_followers), "\n", existing_followers)
        if action == 'follow':
            users_with_tweets = users_with_tweets()
            print("\nusers_with_tweets :", len(users_with_tweets), "\n", users_with_tweets)
            users_to_follow = (users_with_tweets - (existing_followers.union(existing_followings)))
            print("\nusers_to_follow :", len(users_to_follow), "\n", users_to_follow)
            follow_user(users_to_follow, sleep)
        elif action =='follow_followers':
            users_to_follow = existing_followers - existing_followings
            print("\nusers_to_follow :", len(users_to_follow), "\n", users_to_follow)
            follow_user(users_to_follow, sleep)
        elif action == 'pm':
            if pm:
                send_private_message(existing_followers, sleep, pm)
            else:
                print("\nPlease specify message which should be sent to followers. Use --pm 'text zpravy'")
        else:
            users_to_unfollow = existing_followings - existing_followers
            print("\nusers_to_unfollow :", len(users_to_unfollow), "\n", users_to_unfollow)
            unfollow_user(users_to_unfollow, sleep)
        print("\nDone...")

    except tweepy.TweepError as e:
        e = eval(str(e))
        print(e[0]['message'], "| Code :", e[0]['code'])
