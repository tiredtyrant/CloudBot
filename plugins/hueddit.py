from datetime import datetime
import re
import random
import asyncio
import functools
from urllib.parse import urlparse

import praw, prawcore
import requests

from cloudbot import hook
from cloudbot.util import timeformat, formatting

@hook.on_start
def reddit_login(bot):
    global reddit_instance 
    reddit_instance = praw.Reddit(client_id=bot.config.get("api_keys", {}).get("reddit_client_id", None),
            client_secret=bot.config.get("api_keys", {}).get("reddit_client_secret", None),
            user_agent=bot.config.get("api_keys", {}).get("reddit_user_agent", None),
            username=bot.config.get("api_keys", {}).get("reddit_username", None),
            password=bot.config.get("api_keys", {}).get("reddit_password", None))
            
def is_image(url):
    parsed = urlparse(url)
    splitted = parsed.path.split('.')
    if len(splitted) > 1 and splitted[1] in ['jpg', 'gifv', 'gif', 'jpeg', 'png'] or 'gfycat' in parsed.netloc:
        return True
    else:
        return False

def get_image(sublist):

    MAX_IMAGE_LIST = 50
    LIMIT_NO_IMG = 50

    # get a random sub, and check if valid.
    foundsub = False
    while not foundsub:
        if not len(sublist):
            raise praw.exceptions.PRAWException('No valid subreddits')
        subname = random.choice(sublist)
        sub = reddit_instance.subreddit(subname)
        try:
            sub.subreddit_type
        except (prawcore.exceptions.Forbidden, prawcore.exceptions.NotFound) as e:
            # if subreddit is private or banned, remove from list and pick another one
            sublist.remove(subname)
            continue
        foundsub = True

    submlist = []

    for index, submission in enumerate(sub.hot(limit=900)):
        if not submission.is_self and is_image(submission.url):
            submlist.append(submission)

        if len(submlist) >= MAX_IMAGE_LIST:
            break

        # give up if couldn't find any images in the first LIMIT_NO_IMG submissions
        if index > LIMIT_NO_IMG and len(submlist) == 0:
            break

    if submlist:
        return random.choice(submlist)
    else:
        raise praw.exceptions.PRAWException('Could not find image')

def get_displayline(submission):
    return '{} ( {} - {} - {} ) {}'.format(submission.url, submission.subreddit_name_prefixed, submission.title, submission.shortlink, ' \x0304NSFW' if submission.over_18 else '')

def do_search(sublist):
    try:
        subm = get_image(sublist)
    except praw.exceptions.PRAWException as e:
        return e
    return get_displayline(subm)

@hook.command('pic', 'img')
def reddit_random_image_search(text):
    return do_search([text])
    
@hook.command('bork')
def random_bork_search():
    subs = ['woof_irl', 'woofbarkwoof', 'supershibe', 'rarepuppers', 'dogpictures', 'doggos', 'surpriseddogs', 'dogbridges']
    return do_search(subs)

@hook.command('meow','miau')
def random_meow_search():
    subs = ['catsstandingup', 'catpictures', 'kitty', 'cats', 'catsinbusinessattire', 'meow_irl', 'greebles', 'catculations']
    return do_search(subs)

@hook.command('omnomnom','nom')
def random_nom_search():
    subs = ['gifrecipes','foodporn']
    return do_search(subs)

@hook.command('quack')
def random_duck_search():
    subs = ['duck']
    return do_search(subs)

@hook.command('loro', 'currupaco', 'piu')
def random_birb_search():
    subs = ['birbs', 'partyparrot', 'parrots', 'illegallysmolbirbs']
    return do_search(subs)

@hook.command('oinc')
def random_pig_search():
    subs = ['pigs', 'babypigs', 'pigtures', 'pigifs']
    return do_search(subs)

@hook.command('bnf')
def random_feneco_search():
    #subs = ['fennecfoxes']
    #return do_search(subs)
    return 'https://media.tenor.com/9TLMQmXGRGwAAAAd/floof-foxo.gif'

@hook.command('bnt')
def random_tjader_search():
    subs = ['pizza', 'pizzacrimes']
    return do_search(subs)

@hook.command('bng')
def random_goika_search():
    subs = ['natureporn', 'forest', 'outdoors', 'hiking']
    return do_search(subs)

@hook.command('glub')
def random_glub_search():
    subs = ['hydrohomies']
    return do_search(subs)
