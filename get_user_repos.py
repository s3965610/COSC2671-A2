"""Script focuses on getting the repositories that have been starred per user. Due to API limits we take in the 2090 users and for each we only get their first 100"""

import json

import requests

API_KEY = '<ENTER YOU API KEY HERE>'

GH_API_ENDPOINT = 'https://api.github.com/graphql'

USER_REPO_QUERY = '''
query($uname: String!) {
  user(login: $uname) {
    starredRepositories(orderBy: {field: STARRED_AT, direction: ASC}, first: 100) {
      totalCount
      nodes {
        nameWithOwner
      }
    }
  }
}'''


def load_user_logins(filename):
    with open(filename) as fp:
        data = [line.strip() for line in fp.readlines()[1:]]
        return data


def save_user_repos(data, filename):
    # Get any user_repos already saved
    with open(filename) as fp:
        try:
            curr_data = json.load(fp)
            data.update(curr_data)
            # data = {**curr_data, **data}
        except:
            pass  # TODO: handle exception

    with open(filename, 'w') as fp:
        json.dump(data, fp)


def get_user_repos(login):
    payload = {
        'query': USER_REPO_QUERY,
        'variables': {
            'uname': login
        },
    }

    headers = {
        'Authorization': 'Bearer {}'.format(API_KEY)
    }

    r = requests.post(GH_API_ENDPOINT, json=payload, headers=headers)
    res = r.json()
    return res


logins = load_user_logins('./data/logins.csv')
user_repos = {}
# track the current user in case API rate limit gets hit. (TODO: replace w/ proper checks)
curr = 0
while curr < len(logins):
    try:
        repos = get_user_repos(logins[curr])
        user_repos[logins[curr]] = repos
    except Exception as e:
        print(e)
        break

    curr += 1

# Write what we have to file
save_user_repos(user_repos, './data/user_repos.json')

print(f'Current User: {curr}')
