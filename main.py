import os
import requests
import re
from dotenv import load_dotenv
import argparse


def expand_shotlink(token, bitlink_id):
    headers = {
        'Authorization': 'Bearer {}'.format(token)
    }
    data = {
        'bitlink_id': bitlink_id,
    }
    url = 'https://api-ssl.bitly.com/v4/expand'

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

    return response.json()['link']


def get_shotlink(token, long_url):
    headers = {
        'Authorization': 'Bearer {}'.format(token)
    }
    data = {
        'long_url': long_url,
    }
    url = 'https://api-ssl.bitly.com/v4/bitlinks'

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 400:
        return False
    response.raise_for_status()

    return response.json()['link']


def get_clicks(token, bitlink):
    headers = {
        'Authorization': 'Bearer {}'.format(token)
    }
    data = {
        'unit': 'month',
        'units': -1
    }
    url = 'https://api-ssl.bitly.com/v4//bitlinks/{}/clicks'.format(bitlink)

    response = requests.get(url, headers=headers, data=data)
    if response.status_code in (403, 404):
        return False
    response.raise_for_status()

    total = sum(x['clicks'] for x in response.json()['link_clicks'])
    return total


def get_clicks_or_shortlink(token, link):
    short_link = re.sub(r"https?://(.*)", r'\g<1>', link).strip().strip('/')

    clicks = get_clicks(token, short_link)
    if clicks is not False:
        return ('Количество переходов по ссылке битли', clicks)

    short_link = get_shotlink(token, link)
    if short_link:
        return ('', short_link)

    return ('', False)


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(
        description='Получает короткую ссылку или количество кликов'
    )
    parser.add_argument('link', help='Ссылка')
    args = parser.parse_args()

    token = os.getenv("TOKEN")
    # print('Введите длинную ссылку для её сокращения или короткую для получения количества кликов по ней: ', end='')
    # link = input()
    link = args.link

    (result_type, result) = get_clicks_or_shortlink(token, link)
    print("{}: {}".format(result_type, result) if result else "Некоректная ссылка")


if __name__ == '__main__':
    main()
