import requests

url = 'https://www.google.co.jp/'
response = requests.get(url)
print(response.text)