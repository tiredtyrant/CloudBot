from cloudbot import hook
from cloudbot.util import colors
import requests

#https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=USD&include_24hr_change=true

@hook.command("btc","bitcoin",autohelp=False)
def huecoin(message, bot, conn):
    params = {
        'ids': 'bitcoin',
        'vs_currencies': 'USD',
        'include_24hr_change': 'true'
    }
    headers = {'User-Agent': bot.user_agent}
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price", params=params, headers=headers)
        r.raise_for_status()
        response = r.json()
    except Exception:
        return("rip .btc")
        print(response)
        raise
        
    #example:
    #{
    #  'bitcoin': {
    #    'usd': 9173.02, 
    #    'usd_24h_change': -0.24865295786135225
    #    }
    #}
    value = colors.parse('$(orange)${:,.2f}$(clear)'.format(response['bitcoin']['usd']))
    change = response['bitcoin']['usd_24h_change'];
    fchange = float(change);
    
    if fchange < 0:
        changestr = colors.parse("$(dark_red){:.3}%$(clear)".format(fchange))
    elif fchange > 0:
        changestr = colors.parse("$(dark_green)+{:.3}%$(clear)".format(fchange))
    else:
        changestr = " {:.3}%".format(fchange)
        
    return "1 BTC: {} USD - {}".format(value, changestr);
    
