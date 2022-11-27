from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel
from APIs import FoodData, KrogerCustomer, Kroger, Spoonacular
from datetime import datetime
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Optional

app = FastAPI()

app.mount('/static', StaticFiles(directory='static'), name='static')

templates = Jinja2Templates(directory='templates')


class GroceryItem(BaseModel):
    item: str
    quantity: int

db = {}

@app.get('/', response_class=HTMLResponse)
def welcome(request: Request):
    return templates.TemplateResponse('welcome.html', context={'request':
                                                                  request,
                                                    'message': 'Welcome'})

@app.get('/macros', response_class=HTMLResponse)
def get_macro_form(request: Request):
    result = "Enter macros"
    return templates.TemplateResponse("macros.html", {"request": request,
                                                          "result": result})


@app.post('/macros', response_class=RedirectResponse)
def post_macro_form(request: Request, carbs: int = Form(), protein :
                            int = Form(), fat : int = Form()):
    url = f"{app.url_path_for('get_macro_recs')}?carbs={carbs}&pr" \
          f"otein={protein}&fat={fat}"
    response = RedirectResponse(url=url)
    response.status_code = 301
    return response


@app.get('/macros-results', response_class=HTMLResponse)
def get_macro_recs(request: Request, carbs, protein, fat):
    result = FoodData.food_from_macros(int(carbs), int(protein), int(fat))
    return templates.TemplateResponse("macroResults.html", {"request": request,
                                                          "result": result})


@app.get('/food-search', response_class=HTMLResponse)
def get_food(request: Request):
    result = "Enter a food item"
    return templates.TemplateResponse("foodSearch.html", {"request": request,
                                                      "result": result})

@app.post('/food-search', response_class=RedirectResponse)
def post_food(request: Request, food: str = Form()):
    url = f"{app.url_path_for('get_food_macros')}?food={food}"
    response = RedirectResponse(url=url)
    response.status_code = 301
    return response


@app.get('/food-search-results', response_class=HTMLResponse)
def get_food_macros(request: Request, food):
    result = FoodData.get_food(food)
    return templates.TemplateResponse("foodSearch.html", {"request": request,
                                                      "result": result})


@app.get('/recipe-search', response_class=HTMLResponse)
def get_recipe(request: Request):
    result = "Search for a recipe"
    return templates.TemplateResponse("recipeSearch.html", {"request": request,
                                                      "result": result})

@app.post('/recipe-search', response_class=HTMLResponse)
def post_recipe(request: Request, ingredient1 : str = Form(None), ingredient2: str
                        = Form(None), ingredient3 : str = Form(None), carbs :
                        int = Form(None), protein : int = Form(None), fat : int = Form(None)):
    if any([ingredient1, ingredient2, ingredient3]):
        url = f"{app.url_path_for('get_recipes_ingredients')}?ingredient1=" \
              f"{ingredient1}&ingredient2={ingredient2}&ingredient3={ingredient3}"
        response = RedirectResponse(url=url)
        response.status_code = 301
        return response
    else:
        if carbs is None or protein is None or fat is None:
            result = "Please enter all macros"
            return templates.TemplateResponse("recipeSearch.html",
                                              {"request": request,
                                               "result": result})
        else:
            url = f"{app.url_path_for('get_recipes_macros')}?carbs=" \
                  f"{carbs}&protein={protein}&fat={fat}"
            response = RedirectResponse(url=url)
            response.status_code = 301
            return response


@app.get('/recipes-from-ingredients', response_class=HTMLResponse)
def get_recipes_ingredients(request: Request, ingredient1, ingredient2,
                        ingredient3):
    to_search = []
    for i in [ingredient1, ingredient2, ingredient3]:
        if i != 'None':
            to_search.append(i)

    result = Spoonacular.get_recipe_from_ingredients(i)
    return templates.TemplateResponse("recipeSearch.html", {"request": request,
                                                      "result": result})

@app.get('/recipes-from-macros', response_class=HTMLResponse)
def get_recipes_macros(request: Request, carbs, protein, fat):
    result = Spoonacular.get_recipes_from_macros(carbs, protein, fat)
    return templates.TemplateResponse("recipeSearch.html", {"request": request,
                                                      "result": result})


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
    # url = app.url_path_for('kroger_login_successful')
    url = app.url_path_for('get_add_to_cart')
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
    url = app.url_path_for('get_add_to_cart')
    response = RedirectResponse(url=url)
    return response


@app.get('/Kroger/login-successful')
def kroger_login_successful():
    return 'successfully logged in!'


# for testing purposes only
@app.get('/Kroger/all-codes')
def get_kroger_tokens():
    return db


@app.get('/Kroger/set-preferred-location/', response_class=HTMLResponse)
def get_location(request: Request):
    result = "Enter zipcode and chain"
    return templates.TemplateResponse('SetLocation.html', {"request": request,
                                                         "result": result})

@app.post('/Kroger/set-preferred-location/', response_class=RedirectResponse)
def post_location(request: Request, zipcode : str = Form(), chain : str =
                        Form()):
    url = f"{app.url_path_for('set_preferred_location')}?zipcode=" \
          f"{zipcode}&chain={chain}"
    response = RedirectResponse(url=url)
    response.status_code = 301
    return response

@app.get('/Kroger/set-preferred-location-result', response_class=HTMLResponse)
def set_preferred_location(request: Request, zipcode, chain):
    preferred_location = Kroger.get_Kroger_location(zipcode, chain)
    db['preferred_location_id'] = preferred_location['locationId']
    db['preferred_location_chain'] = preferred_location['chain']
    db['preferred_location_address'] = preferred_location['address']
    result = f"Added preferred {db['preferred_location_chain']} at " \
             f"{db['preferred_location_address']['addressLine1']} " \
             f"{db['preferred_location_address']['city']} " \
             f"{db['preferred_location_address']['state']} " \
             f"{db['preferred_location_address']['zipCode']} "
    return templates.TemplateResponse('setLocation.html', {"request": request,
                                                         "result": result})



@app.get('/Kroger/add-to-cart/', response_class=HTMLResponse)
def get_add_to_cart(request: Request):
    result = "Enter item and quantity"
    return templates.TemplateResponse('addToCart.html', {"request": request,
                                                      "result": result})

@app.post('/Kroger/add-to-cart/', response_class=RedirectResponse)
def post_add_to_cart(request: Request, item : str = Form(), quantity : int =
                        Form()):
    url = f"{app.url_path_for('add_to_cart')}?item={item}&quantity={quantity}"
    response = RedirectResponse(url=url)
    response.status_code = 301
    return response


@app.get('/Kroger/add-to-cart-result', response_class=HTMLResponse)
def add_to_cart(request: Request, item: str, quantity: int, zipcode: str=None, \
                                                                    chain: str=None):
    # if no preferred location, get location using zipcode and chain and save
    # check product availability at preferred location id
    # if available, then add to cart
    if 'kroger_access_token' not in db:
        result = 'please sign in to Kroger first'
        url = app.url_path_for('kroger_sign_in')
        response = RedirectResponse(url=url)
        response.status_code = 301
        return response

    # check if token is expired. if so, make refresh token call
    time_diff = datetime.now() - db['kroger_access_token_start']
    if time_diff.total_seconds() >= 1740:
        refresh_kroger_token()
        db['refreshed'] += 1

    if 'preferred_location_id' in db:
        location_id = db['preferred_location_id']
    elif zipcode is None or chain is None:
        result =  "no preferred location please add"
        url = app.url_path_for('get_location')
        response = RedirectResponse(url=url)
        response.status_code = 301
        return response
        # return templates.TemplateResponse('addToCart.html', {"request": request,
        #                                                      "result": result})
    # else:
    #     location_id = set_preferred_location(zipcode, chain)

    availability_details = Kroger.check_product_availability(item, location_id)

    if availability_details[0]:
        product_id = availability_details[1]['productId']
        kroger_response = KrogerCustomer.add_to_cart(db['kroger_access_token'],
                                       product_id, quantity)

        if 200 < kroger_response.status_code < 300:
            result = f"{item} added"
        else:
            result = "error adding to cart"

        return templates.TemplateResponse('addToCart.html', {"request": request,
                                                         "result": result})