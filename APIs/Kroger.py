import requests
import json
from APIs import config

def auth_client():
    url = 'https://api.kroger.com/v1/connect/oauth2/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Authorization': f"Basic {config.kroger_encoded_client_info}"}
    data = {'grant_type': 'client_credentials', 'scope': 'product.compact'}
    response = requests.post(url, headers=headers, data=data)
    access_token = response.json()['access_token']
    return access_token

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
        f"{chain.upper()}", 'filter.limit': '1'}
    response = requests.get(url, headers=headers, params=query_string)
    stores = response.json()

    if 'data' not in stores or len(stores['data']) == 0:
        return "Try a different zipcode and/or chain"

    result = stores['data'][0]
    return result


def check_product_availability(product=None, location_id=None):
    if product is None:
        return "Please enter product"
    if location_id is None:
        return "Please enter location"

    # check db for access token
    access_token = auth_client()
    url = 'https://api.kroger.com/v1/products'
    headers = {'Accept': 'application/json', 'Authorization': f"Bearer "
                                                              f"{access_token}"}
    query_string = {'filter.term': f"{product}", 'filter.locationId':\
                        f"{location_id}", 'filter.limit': '5'}

    response = requests.get(url, headers=headers, params=query_string)
    response_json = response.json()

    if 'data' in response_json:
        products = response_json['data']

        for product in products:
            item = {'Name': product['description']}
            inventory_details = product['items'][0]
            if 'inventory' in inventory_details:
                if inventory_details['inventory']['stockLevel'] != \
                        'TEMPORARILY_OUT_OF_STOCK':
                    item['productId'] = product['productId']
                    return True, item
            elif any([value for key, value in inventory_details[
                'fulfillment'].items()]):
                item['fulfillment_options'] = [key for key, value in
                                               inventory_details['fulfillment'].items() if value]
                item['productId'] = product['productId']
                return True, item

    return False, {}
