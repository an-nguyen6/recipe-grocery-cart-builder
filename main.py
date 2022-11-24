from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from APIs import FoodData, KrogerCustomer, Kroger
from datetime import datetime

app = FastAPI()

class GroceryItem(BaseModel):
    item: str
    quantity: int

db = {}

@app.get('/')
def hello():
    return {'hello': 'world'}

@app.get('/food/{food_search}')
def get_food(food_search: str):
    food_result = FoodData.get_food(food_search)
    return food_result

@app.get('/food-from-macros/{carb}&{protein}&{fat}')
def food_from_macros(carb: int, protein: int, fat: int):
    food_results = FoodData.food_from_macros(carb, protein, fat)
    return food_results

@app.get('/Kroger', response_class=RedirectResponse)
def kroger_sign_in():
    url = KrogerCustomer.kroger_sign_in()
    return url

@app.get('/Kroger/access-code/', response_class=RedirectResponse)
def get_kroger_token(code: str):
    token_dict = KrogerCustomer.get_token(code)
    db['kroger_access_token'] = token_dict['access_token']
    db['kroger_refresh_token'] = token_dict['refresh_token']
    db['kroger_access_token_start'] = token_dict['start_time']
    url = app.url_path_for('kroger_login_successful')
    response = RedirectResponse(url=url)
    return response

@app.get('/Kroger/refresh-customer-token/', response_class=RedirectResponse)
def refresh_kroger_token():
    new_token_dict = KrogerCustomer.refresh_token(db['kroger_refresh_token'])
    db['kroger_access_token'] = new_token_dict['access_token']
    db['kroger_refresh_token'] = new_token_dict['refresh_token']
    db['kroger_access_token_start'] = new_token_dict['start_time']
    # redirect to add to cart call since this is the only case in which we'd
    # need to refresh the customer access token to reduce number of Kroger
    # signins
    url = app.url_path_for('add_to_cart')
    response = RedirectResponse(url=url)
    return response


@app.get('/Kroger/login-successful')
def kroger_login_successful():
    return 'successfully logged in!'

@app.get('/Kroger/add-to-cart-successful')
def kroger_add_cart_successful():
    return 'successfully added to cart!'

@app.get('/Kroger/add-to-cart-error')
def kroger_add_cart_error():
    return 'There was an error adding to cart!'

# for testing purposes only
@app.get('/Kroger/all-codes')
def get_kroger_tokens():
    return db


@app.post('/Kroger/set-preferred-location')
def set_preferred_location(zipcode, chain):
    preferred_location = Kroger.get_Kroger_location(zipcode, chain)
    db['preferred_location_id'] = preferred_location['locationId']
    db['preferred_location_chain'] = preferred_location['chain']
    db['preferred_location_address'] = preferred_location['address']
    return db['preferred_location_id']


@app.get('/Kroger/add-to-cart/')
def add_to_cart(item: str, quantity: int, zipcode: str=None, chain: str=None):
    # if no preferred location, get location using zipcode and chain and save
    # check product availability at preferred location id
    # if available, then add to cart

    # check if token is expired. if so, make refresh token call
    time_diff = datetime.now() - db['kroger_access_token_start']
    if time_diff.total_seconds() >= 1740:
        refresh_kroger_token()
        db['refreshed'] += 1

    if 'preferred_location' in db:
        location_id = db['preferred_location']
    elif zipcode is None or chain is None:
        return "no preferred location please add zip and chain"
    else:
        location_id = set_preferred_location(zipcode, chain)

    availability_details = Kroger.check_product_availability(item, location_id)

    if availability_details[0]:
        product_id = availability_details[1]['productId']
        kroger_response = KrogerCustomer.add_to_cart(db['kroger_access_token'],
                                       product_id, quantity)

        if 200 < kroger_response.status_code < 300:
            return f"{item} added"
        else:
            return "error adding to cart"

