from http import HTTPStatus

import requests
from bs4 import BeautifulSoup as bs


def find_tags(url):
    response = requests.get(url)
    status_code = response.status_code
    if status_code != HTTPStatus.OK:
        raise ValueError
    else:
        soup = bs(response.text, 'html.parser')
        title = soup.title
        title = '' if not title else title.text
        h1 = soup.h1
        h1 = '' if not h1 else h1.text
        description = soup.find('meta', attrs={'name': 'description'})
        description = '' if not description else description['content']
        return {'title': title, 'h1': h1,
                'description': description}
