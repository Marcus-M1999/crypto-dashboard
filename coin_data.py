 #This example uses Python 2.7 and the python-request library.

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
# import pprint

url = 'https://data.messari.io/api/v1/assets/btc/metrics'
parameters = {
  'start':'1',
  'limit':'5000',
  'convert':'USD',
  # 'symbol':'BTC'
}

# headers = {
#   'Accepts': 'application/json',
#   'X-CMC_PRO_API_KEY': '2ce7f61e-9123-44f3-be2b-a5f99fdfddb6',
# }

session = Session()
# session.headers.update(headers)

try:
  response = session.get(url, params=parameters)
  data = json.loads(response.text)
  
  print(json.dumps(data, indent=4, sort_keys=True))
except (ConnectionError, Timeout, TooManyRedirects) as e:
  print(e)
