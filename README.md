# COSC2671-A2

COSC2671_A2_EDA.ipynb - Exploratory data analysis

community_detection_language.ipynb - Community detection languages.

SNA-graph-follower-following.ipynb - social networks analysis.

rec-sys-baseline.ipynb - analysis for recommender systems

## Data Collection Scripts

- get_ego_nets.py - gathers data to be used for egonets

- get_trending_data.py - gathers data from todays trending page

- get_user_info.py - gathers user informations for supplied unames

- get_user_logins.py - retrieves user identifiers

- get_user_repos.py - retrieves repositories given user identifiers


## Data

- `./data/treding/*` - trending data collected over two days, used as a jump-off point for further analysis
- `./data/logins.csv` - single column csv containing definitive list of logins (usernames) for each user.
- `./data/user_info.json` - contains user information that can be used to derive features & networks
- `./data/user_repos.json` - contains repos that a given user has starred
- `./data/user-items-graph.graphml` - a sample graph of the suers and items
- `./data/user
