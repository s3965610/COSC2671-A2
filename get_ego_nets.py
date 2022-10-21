import requests
from collections import Counter
import pandas as pd
import json
from os import path

# Constants
API_KEY = '<ENTER YOUR API KEY HERE>'
GH_API_ENDPOINT = 'https://api.github.com/graphql'

# Collect the followers and followees for current user


def fetch_user_data(uname):
    # Note: timeouts occur when `first` params are increased
    query = '''
    query($uname: String!) {
      user(login: $uname) {
        followers(first: 25) {
          nodes {
            login
            starredRepositories(orderBy: {field: STARRED_AT, direction: ASC}, first: 100) {
              nodes {
                nameWithOwner
              }
            }
          }
        }
        following(first: 25) {
          nodes {
            login
            starredRepositories(orderBy: {field: STARRED_AT, direction: ASC}, first: 100) {
              nodes {
                nameWithOwner
              }
            }
          }
        }
      }
    }
    '''
    payload = {
        'query': query,
        'variables': {
            'uname': uname
        }
    }
    headers = {
        'Authorization': 'Bearer {}'.format(API_KEY)
    }
    r = requests.post(GH_API_ENDPOINT, json=payload, headers=headers)
    return r.json()


# With the data we can now use Counter to find most starred from following
def get_assoc_repo_names(data):
    """Extracts associated repos given nodes from GH API for follower or following and returns a Counter."""
    top_repos = []
    for user in data:
        for srepos in user['starredRepositories']:
            for srepo in srepos:
                top_repo_names.append(srepo['nameWithOwner'])
    return Counter(top_repos)


def get_top_repos_in_system(top_repos, repos):
    """Extracts only those repos who are in the rec sys repos"""
    repo_recs = []
    for name, count in top_repos.items():
        if name in set(repos['repos']):
            repo_recs.append((name, count))
    return repo_recs


if __name__ == '__main__':
    idx = -1
    all_users = pd.read_csv('./top_users.csv')
    all_repos = pd.read_csv('./top_repos.csv')
    all_users = list(all_users['user'])
    for user in all_users:
        print(f'Processing user: {user}')
        idx += 1

        if path.exists('./data/egonets/following/'+user+'.json'):
            print('File for user already exists.')
            print('Skipping...')
            continue

        print('Fetching data')
        data = fetch_user_data(user)

        following_data = data['data']['user']['following']
        followers_data = data['data']['user']['followers']

        print('Saving data')
        if following_data:
            # Save user following
            with open('./data/egonets/following/'+user+'.json', 'w') as fp:
                json.dump(following_data, fp)

        if followers_data:
            # Save user followers
            with open('./data/egonets/followers/'+user+'.json', 'w') as fp:
                json.dump(followers_data, fp)

        print('Done.')
        # top_repos = get_assoc_repo_names(data)

    print(f'Final idx: {idx}')
