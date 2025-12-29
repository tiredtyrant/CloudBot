from datetime import datetime
import requests
from bs4 import BeautifulSoup
from cloudbot import hook
from cloudbot.util import colors

URL = 'https://steamdb.info/sales/history/'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'
}

@hook.command('sale', 'nextsale', autohelp=False)
def get_sale_data():
    """returns the next or current steam sale date"""

    request = requests.get(URL, headers=HEADERS)
    html = request.text
    soup = BeautifulSoup(html, 'html.parser')

    if soup.find("span", "sale-name"):
        sale_name = soup.find("span", "sale-name").string
        if soup.select_one("h3 > span.sale-unconfirmed"):
            status = soup.find("span", "sale-unconfirmed").contents[-1].strip()
        else:
            status = 'Confirmed'
        temp_date = soup.find("h3").contents[2].strip(' on')

    elif soup.find("div", "next-sale"):
        status = 'Active'
        sale_name = soup.find("h2").string
        temp_date = soup.find("h3").contents[0].strip('runs until')

    else:
        return "Something went wrong."

    temp_date = datetime.strptime(temp_date + " 15", "%d %B %Y %H")
    time = str(temp_date - datetime.now()).partition('.')[0]
    date = datetime.strftime(temp_date, "%B %d, %Y")

    return colors.parse("$(bold){}$(clear) {} $(bold){}$(clear) ({} {}) [{}]".format(sale_name,
                                                                                     'on' if status != 'Active' else 'runs until',
                                                                                     date,
                                                                                     time,
                                                                                     'left' if status == 'Active' else 'from now',
                                                                                     status)
                        )
