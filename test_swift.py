import requests
import json
from flask import jsonify

url = 'http://127.0.0.1:5000/swift'
response = requests.post(url, json="[\"Settings\", \"Location\"]")

if response.status_code == 200:
    print('POST request successful')
    print('request get:')
    print(requests.get(url).text)

else:
    print('POST request failed')