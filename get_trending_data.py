"""Program gets the HTML text for trending page for current day then extracts data and stores as JSON file."""

from datetime import date
import os
import requests
from bs4 import BeautifulSoup
import json

# URL for GitHub trending page subset to English lanuage repositories.
GITHUB_TRENDING_URL = 'https://github.com/trending?spoken_language_code=en'

# Root data directory
DATA_DIR = './data/trending/'


def get_current_trending_page(file):
    """Function retrieves html page for giveGitHub trending page. First tries to read from filesystem if exists, otherwise gets from GitHub directly."""
    # try get from local filesystem first
    if os.path.exists(file):
        with open(file, 'r') as fp:
            return fp.read()

    return download_trending_page(file)


def download_trending_page(file=None):
    """Function GET request from GITHUB_TRENDING_URL 
    optionally writes to content to file and returns content."""
    r = requests.get(GITHUB_TRENDING_URL)
    if file:
        with open(file, 'w') as fp:
            fp.writelines(r.text)
    return r.text


def extract_repo_data(html_text):
    """Takes string of HTML and uses bs4 to extract names and owners of trending repos."""
    soup = BeautifulSoup(html_text, 'html.parser')

    # Gather <article class='Box-row'> these contain data per repo
    articles = soup.find_all('article', attrs={'class': 'Box-row'})
    if (len(articles) < 25):
        print(f'WARNING: Expected 25 got {len(articles)}')

    repos = []
    for article in articles:
        owner, name = [text.strip()
                       for text in article.h1.a.text.strip().split('/')]
        repos.append({'name': name, 'owner': owner})

    return repos


def write_json(datalist, file):
    """Takes a list of dictionaries, wraps with data envelope and writes."""
    data = {
        'data': datalist
    }
    with open(file, 'w') as fp:
        json.dump(data, fp)


def main():
    if not os.path.isdir(DATA_DIR):
        print('Data directory not found, exiting.')
        exit(-1)

    # Setup file paths
    html_path = DATA_DIR + 'trending-page-' + str(date.today()) + '.html'
    json_path = DATA_DIR + str(date.today()) + '.json'

    # Gather, extract, and save data
    html_text = get_current_trending_page(html_path)
    repos = extract_repo_data(html_text)
    write_json(repos, json_path)


if __name__ == '__main__':
    main()
