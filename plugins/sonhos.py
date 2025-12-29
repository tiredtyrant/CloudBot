import random
import re
import requests
import unidecode

from cloudbot import hook
from cloudbot.util import web, formatting
from urllib.parse import quote


@hook.command("sonhos")
def sonhos(text):
    """sonhos <phrase> [id] -- Looks up <phrase> on www.sonhos.com.br."""

    if text:
        # clean and split the input
        text = text.lower().strip()
        parts = text.split()

        # if the last word is a number, set the ID to that number
        if parts[-1].isdigit():
            id_num = int(parts[-1])
            # remove the ID from the input string
            del parts[-1]
        else:
            id_num = 1

        text = "-".join(parts)

        # fetch the definitions
        try:
            url = "http://www.sonhos.com.br/sonhar-com-"+unidecode.unidecode(text)
            request = requests.get(url)
            request.raise_for_status()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
            return "Could not get definition: {}".format(e)

        page = request.text

        definitions = re.findall("<span class=\"text-post\">(.*?)</span>", page, re.DOTALL)

        if definitions:
            try:
                definition = definitions[id_num - 1]
            except IndexError:
                return 'Não encontrado.'
            
            def_found = re.findall("Significado Sonhar com (.+?)<p>", definition, re.DOTALL)
            if len(def_found) == 0: 
                def_found = re.findall("Significado de sonhar com (.+?)\.", definition, re.DOTALL)

            if len(def_found) == 0: 
                def_found = re.findall("<p><p><strong>Sonhar com (.+?)</strong>", definition, re.DOTALL)

            if len(def_found) == 0: 
                def_found = text.capitalize().strip()
            else:
                def_found = def_found[0].capitalize().strip()

            def_text = sanitize(definition)

            short_url = web.try_shorten(url)
            
            output = "[{}/{}] \x02{}\x02: {} - {}".format(id_num, len(definitions), def_found, def_text, short_url)
        else:
            output = 'Não achei nada com o termo \x02' + text + '\x02.'

        return output

def sanitize(definition):
    def_text = re.sub("<p><p><strong>Sonhar com .+?</strong>", "", definition, flags=re.DOTALL)
    def_text = re.sub("Significado de sonhar com .+?\.", "", def_text)
    def_text = re.sub("Significado Sonhar com .+?<p>", "", def_text)
    def_text = re.sub("<script .+?</script>", "", def_text, flags=re.DOTALL)
    def_text = re.sub("<.*?>"," ", def_text, flags=re.DOTALL)
    def_text = re.sub("<br />|<br>"," ", def_text)
    def_text = re.sub("\s+?,", ",", def_text)
    def_text = re.sub("\s+"," ", def_text)
    def_text = re.sub("&nbsp;"," ", def_text)
    l = def_text.splitlines()
    n = [item.strip() for item in l]
    def_text = " ".join(n).strip()
    def_text = formatting.truncate(def_text, 380)

    return def_text
