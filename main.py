from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel
from APIs import FoodData, KrogerCustomer, Kroger, Spoonacular
from datetime import datetime
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from database import DataBase


app = FastAPI()
app.db = DataBase()
app.db.put('refreshed', 0)

app.mount('/static', StaticFiles(directory='static'), name='static')

templates = Jinja2Templates(directory='templates')



@app.get('/', response_class=HTMLResponse)
def welcome(request: Request):
    return templates.TemplateResponse('welcome.html', context={'request':request,
                                        'message': 'Welcome'})

@app.get('/macros', response_class=HTMLResponse)
def get_macro_form(request: Request, message="Enter macros", result={"None":
                                                                         {
                                                                             "results":0}}):
    if 'macro_results' in app.db.all():
        result = app.db.get('macro_results')

    return templates.TemplateResponse("macros.html", {"request": request,
                                                      "message": message,
                                                          "result":
                                                          result})


@app.post('/macros-results', response_class=RedirectResponse)
def post_macro_form(request: Request, carbs: int = Form(), protein :
                            int = Form(), fat : int = Form()):
    if carbs + protein + fat <= 0:
        result = {"None": {"Invalid or no macros entered":0}}
    else:
        result = FoodData.food_from_macros(int(carbs), int(protein), int(fat))[1]
        app.db.put('macro_results', result)
    return templates.TemplateResponse("macros.html", {"request": request,
                                                      "result":
                                                          result})



@app.get('/food-search', response_class=HTMLResponse)
def get_food(request: Request, message="Enter food", result={"None":"yet"}):
    return templates.TemplateResponse("foodSearch.html", {"request": request,
                                                      "message": message, "result": result})

@app.post('/food-search-results', response_class=RedirectResponse)
def post_food(request: Request, food: str = Form()):
    result = FoodData.get_food(food)
    return templates.TemplateResponse("foodSearch.html", {"request": request,
                                                          "result": result})


@app.get('/recipe-search', response_class=HTMLResponse)
def get_recipe(request: Request, message="Search for a recipe", result={
    "None":{"results":0}}):
    return templates.TemplateResponse("recipeSearch.html", {"request": request,
                                                            "message": message,
                                                      "result": result})

@app.post('/recipe-search-ingredients', response_class=HTMLResponse)
def post_recipe(request: Request, ingredient1 : str = Form(None), ingredient2: str
                        = Form(None), ingredient3 : str = Form(None)):
    to_search = []
    for i in [ingredient1, ingredient2, ingredient3]:
        if i != 'None':
            to_search.append(i)

    result = Spoonacular.get_recipe_from_ingredients(to_search)
    return templates.TemplateResponse("recipeSearch.html", {"request": request,
                                                            "result": result})



@app.post('/recipe-search-macros', response_class=HTMLResponse)
def post_recipe(request: Request, carbs :
                        int = Form(None), protein : int = Form(None), fat : int = Form(None)):

    if carbs is None or protein is None or fat is None or carbs < 0 or \
            protein < 0 or fat < 0:
        result = {"None": {"Missing or invalid macros":'please re-enter'}}
        return templates.TemplateResponse("recipeSearch.html",
                                          {"request": request,
                                           "result": result})
    else:
        result = Spoonacular.get_recipes_from_macros(carbs, protein, fat)
        return templates.TemplateResponse("recipeSearch.html",
                                          {"request": request,
                                           "result": result})


@app.get('/Kroger', response_class=RedirectResponse)
def kroger_sign_in():
    url = KrogerCustomer.kroger_sign_in()
    return url

@app.get('/Kroger/access-code/', response_class=RedirectResponse)
def get_kroger_token(code: str):
    token_dict = KrogerCustomer.get_token(code)
    app.db.put('kroger_access_token', token_dict['access_token'])
    app.db.put('kroger_refresh_token', token_dict['refresh_token'])
    app.db.put('kroger_access_token_start', token_dict['start_time'])
    url = app.url_path_for('get_add_to_cart')
    response = RedirectResponse(url=url)
    return response

@app.get('/Kroger/refresh-customer-token/', response_class=RedirectResponse)
def refresh_kroger_token():
    new_token_dict = KrogerCustomer.refresh_token(app.db.get(
                                                      'kroger_refresh_token'))
    app.db.put('kroger_access_token', new_token_dict['access_token'])
    app.db.put('kroger_refresh_token', new_token_dict['refresh_token'])
    app.db.put('kroger_access_token_start', new_token_dict['start_time'])
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
    return app.db.all()
    # return db


@app.get('/Kroger/set-preferred-location/', response_class=HTMLResponse)
def get_location(request: Request, result="Enter zipcode and chain"):
    return templates.TemplateResponse('SetLocation.html', {"request": request,
                                                         "result": result})

@app.post('/Kroger/set-preferred-location-result',
          response_class=RedirectResponse)
def post_location(request: Request, zipcode : str = Form(), chain : str =
                        Form()):
    preferred_location = Kroger.get_Kroger_location(zipcode, chain)
    app.db.put('preferred_location_id', preferred_location['locationId'])
    app.db.put('preferred_location_chain', preferred_location['chain'])
    app.db.put('preferred_location_address', preferred_location['address'])
    result = f"Added preferred {app.db.get('preferred_location_chain')} at " \
             f"{app.db.get('preferred_location_address')['addressLine1']} " \
             f"{app.db.get('preferred_location_address')['city']} " \
             f"{app.db.get('preferred_location_address')['state']} " \
             f"{app.db.get('preferred_location_address')['zipCode']} "
    return templates.TemplateResponse('SetLocation.html', {"request": request,
                                                           "result": result})


@app.get('/Kroger/add-to-cart/', response_class=HTMLResponse)
def get_add_to_cart(request: Request, result="Enter item and quantity"):
    return templates.TemplateResponse('addToCart.html', {"request": request,
                                                      "result": result})

@app.post('/Kroger/add-to-cart-result', response_class=RedirectResponse)
def post_add_to_cart(request: Request, item : str = Form(), quantity : int =
                        Form()):
    # if no preferred location, get location using zipcode and chain and save
    # check product availability at preferred location id
    # if available, then add to cart
    if 'kroger_access_token' not in app.db.all():
        url = app.url_path_for('kroger_sign_in')
        response = RedirectResponse(url=url)
        response.status_code = 301
        return response

    # check if token is expired. if so, make refresh token call
    time_diff = datetime.now() - app.db.get('kroger_access_token_start')
    if time_diff.total_seconds() >= 1740:
        refresh_kroger_token()
        updated_refresh = app.db.get('refreshed') + 1
        app.db.put('refreshed', updated_refresh)

    if 'preferred_location_id' in app.db.all():
        location_id = app.db.get('preferred_location_id')
    else:
        url = app.url_path_for('get_location')
        response = RedirectResponse(url=url)
        response.status_code = 301
        return response

    availability_details = Kroger.check_product_availability(item, location_id)

    if availability_details[0]:
        product_id = availability_details[1]['productId']
        kroger_response = KrogerCustomer.add_to_cart(
            app.db.get('kroger_access_token'),
            product_id, quantity)

        if 200 < kroger_response.status_code < 300:
            result = f"{item} added"
        else:
            result = "error adding to cart"

        return templates.TemplateResponse('addToCart.html', {"request": request,
                                                             "result": result})
    else:
        return templates.TemplateResponse('addToCart.html', {"request": request,
                                                             "result": f"{item} not found"})

