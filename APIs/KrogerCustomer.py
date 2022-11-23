import requests
import json
from datetime import datetime

from APIs import config

def kroger_sign_in():
    base_url = 'https://api.kroger.com/v1/connect/oauth2/authorize'
    scope = 'cart.basic:write'
    response_type = 'code'
    client_id = config.kroger_client_id
    redirect_uri = 'http://127.0.0.1:8000/Kroger/access-code'
    url = f"{base_url}?scope={scope}&response_type=" \
          f"{response_type}&client_id={client_id}&redirect_uri={redirect_uri}"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    return url

def get_token(access_code):
    get_token_url = 'https://api.kroger.com/v1/connect/oauth2/token'
    get_token_headers = {'Content-Type': 'application/x-www-form-urlencoded',\
                         'Authorization': f'Basic'
                                          f' {config.kroger_encoded_client_info}'}
    payload = {'grant_type': 'authorization_code', 'code': access_code,\
                      'redirect_uri': 'http://127.0.0.1:8000/Kroger/access-code',}
    response = requests.post(get_token_url, headers=get_token_headers,
                       data=payload)
    r_json = response.json()
    result = {'access_token': r_json['access_token'], 'refresh_token':\
                r_json['refresh_token'], 'start_time': datetime.now()}
    return result

def refresh_token(refresh_token):
    get_token_url = 'https://api.kroger.com/v1/connect/oauth2/token'
    get_token_headers = {'Content-Type': 'application/x-www-form-urlencoded',\
                         'Authorization': f'Basic'
                                          f' {config.kroger_encoded_client_info}'}
    payload = {'grant_type': 'refresh_token', 'refresh_token': refresh_token}
    response = requests.post(get_token_url, headers=get_token_headers,\
                       data=payload)
    r_json = response.json()
    result = {'access_token': r_json['access_token'], 'refresh_token':\
                r_json['refresh_token'], 'start_time': datetime.now()}
    return result

def add_to_cart(access_token, upc, quantity):
    get_token_url = 'https://api.kroger.com/v1/cart/add'
    get_token_headers = {'Accept': 'application/json',\
                         'Authorization': f"Bearer {access_token}"}
    payload = {'items':
        [{
          "upc": upc,
          "quantity": quantity
          }
        ]}
    response = requests.put(get_token_url, headers=get_token_headers,
                       data=json.dumps(payload))
    return response

