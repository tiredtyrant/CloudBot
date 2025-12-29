import random
import re
import requests

from cloudbot import hook
from cloudbot.util import web, formatting
from urllib.parse import quote


@hook.command("dicionario")
def dicionario(text):
    """dicionario <phrase> [id] -- Looks up <phrase> on dicionarioinformal.com.br."""

    if text:
        # clean and split the input
        text = text.lower().strip()
        parts = text.split()

        # if the last word is a number, set the ID to that number
        if parts[-1].isdigit():
            id_num = int(parts[-1])
            # remove the ID from the input string
            del parts[-1]
            text = " ".join(parts)
        else:
            id_num = 1

        # fetch the definitions
        try:
            url = "http://www.dicionarioinformal.com.br/"+quote(text)
            request = requests.get(url)
            request.raise_for_status()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
            return "Could not get definition: {}".format(e)

        page = request.text

        definitions = re.findall("<p class=\"text-justify\">(.*?)</p>", page, re.DOTALL)
        if definitions:
            try:
                definition = definitions[id_num - 1]
                def_text = sanitize(definition)
            except IndexError:
                return 'Não encontrado.'

            short_url = web.try_shorten(url)
            
            output = "[{}/{}] {} - {}".format(id_num, len(definitions), def_text, short_url)
        else:
            output = 'Não achei nada com o termo \x02' + text + '\x02.'

        return output


def sanitize(definition):
    def_text = re.sub("<strong>|</strong>","\x02", definition)
    def_text = re.sub("<br />|<br>"," ", def_text)
    def_text = re.sub("<.*?>"," ", def_text)
    def_text = re.sub("\s+"," ", def_text)
    l = def_text.splitlines()
    n = [item.strip() for item in l]
    def_text = " ".join(n).strip()
    def_text = formatting.truncate(def_text, 380)

    return def_text
