import requests
import json
from APIs import config


# determine closest Kroger location to user
# check product availability

def auth_client():
    url = 'https://api.kroger.com/v1/connect/oauth2/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Authorization': f"Basic {config.kroger_encoded_client_info}"}
    data = {'grant_type': 'client_credentials', 'scope': 'product.compact'}
    response = requests.post(url, headers=headers, data=data)
    return response.json()['access_token']

def get_Kroger_location(zipcode=None, chain=None):
    # check db for access_token. if not there, then run auth_client
    if zipcode is None:
        return "Please enter a zipcode"
    if chain is None:
        return "Please select a Kroger-owned chain"
    access_token = auth_client()
    url = 'https://api.kroger.com/v1/locations'
    headers = {'Accept': 'application/json', 'Authorization': f"Bearer "
                                                              f"{access_token}"}
    query_string = {'filter.zipCode.near': f"{zipcode}", 'filter.chain':
        f"{chain.upper()}", 'filter.limit': '2'}
    response = requests.get(url, headers=headers, params=query_string)
    stores = response.json()

    if len(stores['data']) == 0:
        return "Try a different zipcode and/or chain"

    result = stores['data']
    return result

def check_product_availability(product=None, location_id=None):
    return None

