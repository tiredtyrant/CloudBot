import requests
from bs4 import BeautifulSoup
from cloudbot import hook
from cloudbot.util import colors, web

def get_items_list(studios):
    """returns string of iterables (genres and studios list)"""
    studios_list = []
    if not studios:
        return r"¯\_(ツ)_/¯"
    for sibling in studios:
        if sibling.name == 'a':
            studios_list.append(sibling.string)
    return ", ".join(studios_list)

def get_episodes(session, anime_page):
    """returns episodes when the anime doesn't have a number for total episodes"""
    try:
        response = session.get(f"{anime_page}/episode")
        response.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
        return "Couldn't get anime data."

    page_content = response.text
    soup = BeautifulSoup(page_content, 'html.parser')

    last_episode = soup.find("span", "di-ib pl4 fw-n fs10").get_text().split("/")[0].strip("(")+"+"

    return last_episode

def get_anime_data(session, anime_page):
    """returns scraped anime data as formatted string"""
    try:
        response = session.get(anime_page)
        response.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
        return "Couldn't get anime data."
    page_content = response.text

    soup = BeautifulSoup(page_content, 'html.parser')

    # scrape
    title = soup.find("h1").string
    title_en = soup.find("p", "title-english title-inherit").text if soup.find("p", "title-english title-inherit") else None
    score = soup.find("div", "score-label").string
    rank = soup.find("span", "numbers ranked").find("strong").string
    medium = soup.find("span", "dark_text", string="Type:").next_sibling.next_sibling.string
    episodes = soup.find("span", "dark_text", string="Episodes:").next_sibling.strip()
    status = soup.find("span", "dark_text", string="Status:").next_sibling.strip()
    aired = soup.find("span", "dark_text", string="Aired:").next_sibling.strip()
    studios = soup.find("span", "dark_text", string="Studios:").next_siblings
    genres = soup.find("span", "dark_text", string="Genres:")
    if genres:
        genres = genres.next_siblings

    # build output
    output = []

    # prettify and formatting
    title_string = f"$(bold){title}$(clear)"
    title_en_string = f"({title_en})" if title_en else None
    medium_string = f"[$(bold){medium}$(clear)]"
    score_string = f"Score: $(bold){score}$(clear)"
    rank_string = f"Rank: $(bold){rank}$(clear)"
    genres_string = f"Genres: $(bold){get_items_list(genres)}$(clear)"
    studios_string = f"Studios: $(bold){get_items_list(studios)}$(clear)"

    # append items to output
    output.append(title_string)

    # some animes don't have english title
    if title_en_string:
        output.append(title_en_string)

    output.append(medium_string)
    output = [" ".join(output)]
    output.extend([score_string, rank_string, genres_string, studios_string])

    # ignore movies' episodes and checks episodes page if ongoing series
    if medium == 'Movie':
        pass
    elif episodes == 'Unknown':
        episodes_string = f'Episodes: $(bold){get_episodes(session, anime_page)}$(clear)'
    else:
        episodes_string = f'Episodes: $(bold){episodes}$(clear)'

    # movies has no episodes
    try:
        output.append(episodes_string)
    except UnboundLocalError:
        pass

    # more formatting
    if status == 'Finished Airing':
        if medium != 'Movie':
            status_string = 'Aired from'
        else:
            status_string = 'Aired'
    else:
        status_string = 'Airing, started'

    if '?' in aired:
        aired_string = aired.strip(' to ?')
        aired_string = f"$(bold){aired_string}$(clear)"
    else:
        aired = aired.replace('to', '$(clear)to$(bold)')
        aired_string = f"$(bold){aired}$(clear)"

    output.append(f"{status_string} {aired_string}")
    output.append(web.try_shorten(anime_page))

    reply = " - ".join(output)

    return reply

@hook.command('myanimelist', 'mal', autohelp=True)
def myanimelist(text):
    """Usage: <anime name>[, index] - Search for anime on myanimelist.net"""
    # treat user input
    cleaned_input = text.strip()
    cleaned_input = text.split(",")
    input_list = [i.strip() for i in cleaned_input]
    anime_input = ' '.join(input_list)
    index = 1

    if len(input_list) > 1 and input_list[-1].isdigit():
        index = int(input_list[-1].strip())
        anime_input = " ".join(input_list[:-1])

    if index <= 0:
        index = 1

    # search anime
    session = requests.Session()
    try:
        response = session.get(f"https://myanimelist.net/search/prefix.json?type=anime&keyword={anime_input}&v=1")
        response.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
        return "Couldn't get anime data."

    json_data = response.json()

    if 'categories' in json_data:
        results_length = len(json_data['categories'][0]['items'])

        if index > results_length:
            index = results_length

        anime_json_data = json_data['categories'][0]['items'][index - 1]
        anime_url = anime_json_data['url']
    else:
        return "Anime not found."

    return colors.parse(f"[{index}/{results_length}] {get_anime_data(session, anime_url)}")
