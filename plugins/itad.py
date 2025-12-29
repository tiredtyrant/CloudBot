# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
import requests
from cloudbot import hook
from cloudbot.bot import bot
from cloudbot.util import colors

# config
key = bot.config.get_api_key("itad")
region = 'br2'
country = 'BR'
shop_list = ['steam', 'gog', 'nuuvem', 'greenmangaming']
since_months = 3 # how many months to check for previous sales in historical data


def convert_to_brl(currency):
    formatted_brl = 'R$ {:,.2f}'.format(currency)
    formatted_brl = formatted_brl.translate(str.maketrans(',.', '.,'))
    return formatted_brl

def shorten_url(url):
    shortened = requests.get('https://is.gd/create.php?format=simple&url={}'.format(url))
    return shortened.text

def get_results(query):
    search_url = 'https://api.isthereanydeal.com/v02/search/search/?key={}&q={}'.format(key, query)
    search_request = requests.get(search_url)
    if search_request.status_code == 200 and search_request.headers['Content-Type'] == 'application/json':
        search_results_json = search_request.json()
        if 'error' in search_results_json:
            return 0
    else:
        return 1
    results = search_results_json['data']['results']
    return results

def get_game_data(results, index=1):
    results_len = len(results)
    plain = results[index - 1]['plain']
    title = results[index - 1]['title']

    output = '[{}/{}] $(bold){}$(clear) '.format(index, results_len, title)
    
    today_timestamp = int(datetime.now().timestamp())
    since_timestamp = since_months * 30 * 24 * 60 * 60
    since = str(today_timestamp-since_timestamp)
    shops = ','.join(shop_list)

    game_prices = 'https://api.isthereanydeal.com/v01/game/prices/?key={}&plains={}&region={}&country={}&shops={}'.format(key, plain, region, country, shops)
    game_overview = 'https://api.isthereanydeal.com/v01/game/overview/?key={}&region={}&country={}&plains={}'.format(key, region, country, plain)
    game_history = 'https://api.isthereanydeal.com/v01/game/lowest/?key={}&plains={}&region={}&country={}&since={}&new=1'.format(key, plain, region, country, since)

    game_prices_request = requests.get(game_prices)
    game_prices_json = game_prices_request.json()

    game_overview_request = requests.get(game_overview)
    game_overview_json = game_overview_request.json()

    game_history_request = requests.get(game_history)
    game_history_json = game_history_request.json()

    if 'price' in game_history_json['data'][plain]:
        recent_low_dict = {
            'price': game_history_json['data'][plain]['price'],
            'date': game_history_json['data'][plain]['added'],
            'store': game_history_json['data'][plain]['shop']['name'],
            'diff': timedelta(seconds=today_timestamp - game_history_json['data'][plain]['added']).days
        }
        
    else:
        recent_low_dict = None

    game_info_url = 'https://isthereanydeal.com/game/{}/info'.format(plain)
    
    if not game_prices_json['data'][plain]['list']:
        output += "No data about this game with the selected stores. More info: {}".format(shorten_url(game_info_url))
        return colors.parse(output)
    
    game_price_list = game_prices_json['data'][plain]['list']
    game_overview_historical_low = game_overview_json['data'][plain]['lowest']

    historical_dict = {
        'price': game_overview_historical_low['price'],
        'date': game_overview_historical_low['recorded_formatted'],
        'store': game_overview_historical_low['store']
    }

    prices_list = []
    for i in game_price_list:
        prices_list.append({'store': i['shop']['name'], 'price_cut': i['price_cut'], 'price_old': i['price_old'], 'price_new': i['price_new'], 'drm': i['drm'], 'url': i['url']})

    prices_string = ''
    price_cut = ''

    for i in prices_list:
        if i['price_cut'] > 0:
            price_cut = ' ($(dgreen, bold)-{}%$(clear), was $(bold){}$(clear))'.format(i['price_cut'], convert_to_brl(i['price_old']))
        else:
            price_cut = '{}%'.format(i['price_cut'])            
        prices_string += '⦁ $(bold){}$(clear): $(bold){}$(clear){} '.format(i['store'], convert_to_brl(i['price_new']), price_cut if i['price_cut'] > 0 else '')

    historical_string = '[$(bold)All time low$(clear): $(bold){}$(clear) on $(bold){}$(clear), {}]'.format(convert_to_brl(historical_dict['price']), historical_dict['store'], historical_dict['date'])
    
    recent_string = '[$(bold)Last {}{}$(clear): $(bold){}$(clear) on $(bold){}$(clear), {} days ago]'.format(since_months if since_months > 1 else '', ' months' if since_months > 1 else 'month', convert_to_brl(recent_low_dict['price']), recent_low_dict['store'], recent_low_dict['diff'])

    output += '{}{} {} - {}'.format(prices_string, historical_string, '' if recent_low_dict == None else recent_string, shorten_url(game_info_url))

    return colors.parse(output)

@hook.command('isthereanydeal', 'itad', autohelp=False)
def isthereanydeal(text):
    """<game title> [, index] - Returns the game entry from isthereanydeal.com"""    
    if text:
        cleaned_query = text.strip()  
        split_query = cleaned_query.split(',')
        cleaned_split_query = [i.strip() for i in split_query]
        actual_query = ' '.join(cleaned_split_query)
        index = 1

        if len(cleaned_split_query) > 1 and cleaned_split_query[-1].isdigit():
            actual_query = ' '.join(cleaned_split_query[:-1])
            index = abs(int(cleaned_split_query[-1]))

        if index < 1:
            index = 1

        results = get_results(actual_query)

        if results == 0:
            return 'Invalid query.'

        if results == 1:
            return 'API failure.'

        if not results:
            return 'No results for "{}".'.format(actual_query)

        if index > len(results):
            index = len(results)

        game_data = get_game_data(results, index)

        return game_data
    return 'Usage: <game title> [, id]'
    
