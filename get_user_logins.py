import requests
import json

API_KEY = '<ENTER YOUR API KEY HERE>'

GH_API_ENDPOINT = 'https://api.github.com/graphql'

# Query expects variables - name: name of repo, owner: owner of repo,
# first: first n watchers, after: cursor for next login
WATCHERS_QUERY = '''
query($name:String!, $owner:String!, $first:Int!, $cursor:String!){
    repository(name: $name, owner: $owner) {
        watchers(first: $first, after: $cursor) {
            edges {
                cursor
                node {
                    login
                }
            }
        }
    }
}
'''


def get_watchers(name, owner, first=100, cursor=""):
    payload = {
        'query': WATCHERS_QUERY,
        'variables': locals(),
    }
    headers = {
        'Authorization': 'Bearer {}'.format(API_KEY)
    }

    r = requests.post(GH_API_ENDPOINT, json=payload, headers=headers)
    res = r.json()
    return res


def load_repos(filename):
    with open(filename, 'r') as fp:
        data = json.load(fp)
        # just return inner list
        return data['data']


def main():
    users = {'data': []}
    repos = load_repos('./data/trending/2022-10-03.json')
    for repo in repos:
        res = get_watchers(repo['name'], repo['owner'])
        watchers = res['data']['repository']['watchers']['edges']
        users['data'] += watchers

    repos = load_repos('./data/trending/2022-10-04.json')
    for repo in repos:
        res = get_watchers(repo['name'], repo['owner'])
        watchers = res['data']['repository']['watchers']['edges']
        users['data'] += watchers

    with open('./data/user_logins.json', 'w') as fp:
        json.dump(users, fp)


if __name__ == '__main__':
    main()
