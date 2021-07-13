# Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
# сохранить JSON-вывод в файле *.json.

import requests
import json

URL = u'https://api.github.com/users/'
USERNAME = 'j2cry'


response = requests.get(f'{URL}{USERNAME}/repos')

print(f'Requesting {URL}{USERNAME}/repos')
if response.status_code != 200:
    exit(f'It seems that something went wrong... (error {response.status_code})')
repositories = response.json()

print(f'User `{USERNAME}` has the following public repositories on GitHub:')
for repo in repositories:
    print(f' * {repo.get("name")}')

with open(f'repos_{USERNAME}.json', 'w') as f:
    json.dump(repositories, f)
print('done. Check out the result.')
