import requests
import json

URL = u'http://api.openweathermap.org/data/2.5/'
API_KEY = 'your own OpenWeatherAPI key'
city = 'Moscow'

response = requests.get(f'{URL}weather?q={city}&appid={API_KEY}')
print('Requesting...')
if response.status_code != 200:
    exit(f'It seems that something went wrong... (error {response.status_code})')

with open(f'weather_{city}.json', 'w') as f:
    json.dump(response.json(), f)
print('done. Check out the result.')
