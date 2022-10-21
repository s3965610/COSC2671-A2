import json
import requests


API_KEY = '<ENTER YOU API KEY HERE>'

GH_API_ENDPOINT = 'https://api.github.com/graphql'

# Query is to retrieve user information that will be used as features for measures of user similarity (18 features in total i think)
USER_INFO_QUERY = '''
query($uname: String!) {
  user(login: $uname) {
    bio
    company
    createdAt
    commitComments {
      totalCount
    }
    followers {
      totalCount
    }
    following {
      totalCount
    }
    gists {
      totalCount
    }
    isGitHubStar
    isHireable
    isEmployee
    isDeveloperProgramMember
    isCampusExpert
    isBountyHunter
    location
    repositories(orderBy: {field: UPDATED_AT, direction: ASC}, first: 10) {
      totalCount
      nodes {
        primaryLanguage {
          name
        }
        repositoryTopics(first: 10) {
          nodes {
            topic {
              name
            }
          }
        }
        labels(first: 10) {
          nodes {
            name
          }
        }
      }
    }
    watching(first: 100) {
      totalCount
    }
  }
}
'''


def save_user_info(data, filename):
    with open(filename, 'r') as fp:
        try:
            curr_data = json.load(fp)
            data.update(curr_data)
        except:
            pass  # TODO: handle exception

    with open(filename, 'w') as fp:
        json.dump(data, fp)


def load_user_logins(filename):
    with open(filename, 'r') as fp:
        data = [line.strip() for line in fp.readlines()[1:]]
        return data


def get_user_info(login):
    payload = {
        'query': USER_INFO_QUERY,
        'variables': {
            'uname': login
        },
    }

    headers = {
        'Authorization': 'Bearer {}'.format(API_KEY)
    }

    r = requests.post(GH_API_ENDPOINT, json=payload, headers=headers)

    res = r.json()
    if r.status_code != 200:
        print(r.text)
    return res, r.status_code


# Collect all unique logins - last time checked it was 2090
logins = load_user_logins('./data/logins.csv')
user_info = {}

curr = 1128  # reset to 0 later... -- user 262, 1127, and another one but dont know which gave error??
while curr < len(logins):
    try:
        uinfo, code = get_user_info(logins[curr])
        if code != 200:
            print(
                f'Recieved code: {code} for request involving user no. {uinfo}')
            print('Continuing...')
        user_info[logins[curr]] = uinfo
    except Exception as e:
        print(e)
        break

    curr += 1

save_user_info(user_info, './data/user_info.json')

print(f'Current User: {curr}')
