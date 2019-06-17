import random
import re
import urllib.parse

import requests

from cloudbot import hook
from cloudbot.bot import bot
from cloudbot.util import web

API_URL = 'http://api.wordnik.com/v4/'
WEB_URL = 'https://www.wordnik.com/words/{}'

ATTRIB_NAMES = {
    'ahd-legacy': 'AHD/Wordnik',
    'ahd': 'AHD/Wordnik',
    'ahd-5': 'AHD/Wordnik',
    'century': 'Century/Wordnik',
    'wiktionary': 'Wiktionary/Wordnik',
    'gcide': 'GCIDE/Wordnik',
    'wordnet': 'Wordnet/Wordnik',
}

# Strings
# TODO move all strings here
no_api = "This command requires an API key from wordnik.com."

# TODO move all api requests to one function, handle status errors


def format_attrib(attr_id):
    try:
        return ATTRIB_NAMES[attr_id]
    except KeyError:
        return attr_id.title() + '/Wordnik'


def sanitize(text):
    return urllib.parse.quote(text.translate({ord('\\'): None, ord('/'): None}))


@hook.command("define", "dictionary")
def define(text):
    """<word> - Returns a dictionary definition from Wordnik for <word>."""
    api_key = bot.config.get_api_key('wordnik')
    if not api_key:
        return no_api

    word = sanitize(text)
    url = API_URL + "word.json/{}/definitions".format(word)

    params = {
        'api_key': api_key,
        'limit': 1
    }
    request = requests.get(url, params=params)
    request.raise_for_status()
    json = request.json()

    if json:
        data = json[0]
        data['word'] = " ".join(data['word'].split())
        data['url'] = web.try_shorten(WEB_URL.format(data['word']))
        data['attrib'] = format_attrib(data['sourceDictionary'])
        return "\x02{word}\x02: {text} - {url} ({attrib})".format(**data)

    return "I could not find a definition for \x02{}\x02.".format(text)


@hook.command("wordusage", "wordexample", "usage")
def word_usage(text):
    """<word> - Returns an example sentence showing the usage of <word>."""
    api_key = bot.config.get_api_key('wordnik')
    if not api_key:
        return no_api

    word = sanitize(text)
    url = API_URL + "word.json/{}/examples".format(word)
    params = {
        'api_key': api_key,
        'limit': 10
    }

    json = requests.get(url, params=params).json()
    if json:
        out = "\x02{}\x02: ".format(text)
        example = random.choice(json['examples'])
        out += "{} ".format(example['text'])
        return " ".join(out.split())

    return "I could not find any usage examples for \x02{}\x02.".format(text)


@hook.command("pronounce", "sounditout")
def pronounce(text):
    """<word> - Returns instructions on how to pronounce <word> with an audio example."""
    api_key = bot.config.get_api_key('wordnik')
    if not api_key:
        return no_api

    word = sanitize(text)
    url = API_URL + "word.json/{}/pronunciations".format(word)

    params = {
        'api_key': api_key,
        'limit': 5
    }
    json = requests.get(url, params=params).json()

    if json:
        out = "\x02{}\x02: ".format(text)
        out += " • ".join([i['raw'] for i in json])
    else:
        return "Sorry, I don't know how to pronounce \x02{}\x02.".format(text)

    url = API_URL + "word.json/{}/audio".format(word)

    params = {
        'api_key': api_key,
        'limit': 1,
        'useCanonical': 'false'
    }
    json = requests.get(url, params=params).json()

    if json:
        url = web.try_shorten(json[0]['fileUrl'])
        out += " - {}".format(url)

    return " ".join(out.split())


@hook.command()
def synonym(text):
    """<word> - Returns a list of synonyms for <word>."""
    api_key = bot.config.get_api_key('wordnik')
    if not api_key:
        return no_api

    word = sanitize(text)
    url = API_URL + "word.json/{}/relatedWords".format(word)

    params = {
        'api_key': api_key,
        'relationshipTypes': 'synonym',
        'limitPerRelationshipType': 5
    }
    json = requests.get(url, params=params).json()

    if json:
        out = "\x02{}\x02: ".format(text)
        out += " • ".join(json[0]['words'])
        return " ".join(out.split())

    return "Sorry, I couldn't find any synonyms for \x02{}\x02.".format(text)


@hook.command()
def antonym(text):
    """<word> - Returns a list of antonyms for <word>."""
    api_key = bot.config.get_api_key('wordnik')
    if not api_key:
        return no_api

    word = sanitize(text)
    url = API_URL + "word.json/{}/relatedWords".format(word)

    params = {
        'api_key': api_key,
        'relationshipTypes': 'antonym',
        'limitPerRelationshipType': 5,
        'useCanonical': 'false'
    }
    json = requests.get(url, params=params).json()

    if json:
        out = "\x02{}\x02: ".format(text)
        out += " • ".join(json[0]['words'])
        out = out[:-2]
        return " ".join(out.split())

    return "Sorry, I couldn't find any antonyms for \x02{}\x02.".format(text)


# word of the day
@hook.command("word", "wordoftheday", autohelp=False)
def wordoftheday(text):
    """[date] - returns the word of the day. To see past word of the day enter use the format yyyy-MM-dd.
    The specified date must be after 2009-08-10."""
    api_key = bot.config.get_api_key('wordnik')
    if not api_key:
        return no_api

    match = re.search(r'(\d\d\d\d-\d\d-\d\d)', text)
    date = ""
    if match:
        date = match.group(1)
    url = API_URL + "words.json/wordOfTheDay"
    if date:
        params = {
            'api_key': api_key,
            'date': date
        }
        day = date
    else:
        params = {
            'api_key': api_key,
        }
        day = "today"

    json = requests.get(url, params=params).json()

    if json:
        word = json['word']
        note = json['note']
        pos = json['definitions'][0]['partOfSpeech']
        definition = json['definitions'][0]['text']
        out = "The word for \x02{}\x02 is \x02{}\x02: ".format(day, word)
        out += "\x0305({})\x0305 ".format(pos)
        out += "\x0310{}\x0310 ".format(note)
        out += "\x02Definition:\x02 \x0303{}\x0303".format(definition)
        return " ".join(out.split())

    return "Sorry I couldn't find the word of the day, check out this awesome otter instead {}".format(
        "http://i.imgur.com/pkuWlWx.gif")


# random word
@hook.command("wordrandom", "randomword", autohelp=False)
def random_word():
    """- Grabs a random word from wordnik.com"""
    api_key = bot.config.get_api_key('wordnik')
    if not api_key:
        return no_api

    url = API_URL + "words.json/randomWord"
    params = {
        'api_key': api_key,
        'hasDictionarydef': 'true',
        'vulgar': 'true'
    }
    json = requests.get(url, params=params).json()
    if json:
        word = json['word']
        return "Your random word is \x02{}\x02.".format(word)

    return "There was a problem contacting the Wordnik API."
