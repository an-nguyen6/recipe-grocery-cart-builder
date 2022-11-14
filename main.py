from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from APIs import FoodData, KrogerCustomer, config

app = FastAPI()

class GroceryItem(BaseModel):
    upc: str
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

@app.get('/Kroger/access-code/')
def get_kroger_token(code: str, request=Request):
    db['kroger_access_token'] = KrogerCustomer.get_token(code)
    return db['kroger_access_token']

@app.get('/Kroger/all_codes')
def get_kroger_tokens():
    return db

@app.post('/Kroger/add-to-cart')
def add_to_cart():
    response = KrogerCustomer.add_to_cart(db['kroger_access_token'],
                                   "0001200016268", 2)
    return response

