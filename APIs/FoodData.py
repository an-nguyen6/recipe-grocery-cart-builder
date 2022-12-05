import requests
from APIs import config

# User adds nutrition preferences (protein, carbs, fat) in grams for a day
# Have a dictionary of general recommendations to meet protein, carbs, and fat
# Pull nutrition info from FoodData for those foods


api_key = config.fd_api_key
food_recommendations = {'high protein': ['chicken', 'beef', 'eggs', 'salmon',
                                         'black beans'], 'high fat': ['olive '
                                                                     'oil',
                                                               'avocado',
                                                               'butter'],
                        'high carb': ['oats', 'rice', ]}


def get_food(search_term):
    base_url = 'https://api.nal.usda.gov/fdc/v1/foods/search'
    url = f"{base_url}?api_key={api_key}&query=" \
          f"{search_term}&dataType=Foundation&pageSize=1"
    response = requests.get(url)
    response_json = response.json()
    result = {}
    has_protein = False
    has_carb = False
    has_fat = False
    has_serving_size = False
    if len(response_json['foods']) > 0:
        nutrients = response_json['foods'][0]['foodNutrients']
        listed_nutrients = [nutrient['nutrientName'] for nutrient
                            in nutrients]
        for ln in listed_nutrients:
            if 'protein' in ln.lower():
                has_protein = True
            if 'fat' in ln.lower():
                has_fat = True
            if 'carb' in ln.lower():
                has_carb = True
        if 'servingSize' in response_json['foods'][0]:
            has_serving_size = True
        if has_protein and has_fat and has_carb and has_serving_size:
            result['Food Name'] = response_json['foods'][0][
                'lowercaseDescription']
            nutrients = response_json['foods'][0]['foodNutrients']
            result['Serving Size'] = f"{response_json['foods'][0]['servingSize']}" \
                                     f" {response_json['foods'][0]['servingSizeUnit']}"
            result['Protein'] = [f"{nutrient['value']}" \
                                 f" {nutrient['unitName'].lower()}" for
                                 nutrient in nutrients if 'protein' in
                                 nutrient['nutrientName'].lower()][0]
            result['Fat'] = [f"{nutrient['value']}" \
                             f" {nutrient['unitName'].lower()}" for
                             nutrient in nutrients if 'fat' in nutrient[
                                 'nutrientName'].lower()][0]
            result['Carbs'] = [f"{nutrient['value']}" \
                               f" {nutrient['unitName'].lower()}" for
                               nutrient in nutrients if 'carb' in nutrient[
                                   'nutrientName'].lower()][0]
            return result

    if result == {}:
        has_protein = False
        has_carb = False
        has_fat = False
        has_serving_size = False
        # do a general search and loop through a few, up to 5 to find something
        url = f"{base_url}?api_key={api_key}&query=" \
              f"{search_term}&pageSize=5"
        response = requests.get(url)
        response_json = response.json()
        for food_item in response_json['foods']:
            result = {}
            nutrients = food_item['foodNutrients']
            listed_nutrients = [nutrient['nutrientName'] for nutrient
                               in nutrients]
            for ln in listed_nutrients:
                if 'protein' in ln.lower():
                    has_protein = True
                if 'fat' in ln.lower():
                    has_fat = True
                if 'carb' in ln.lower():
                    has_carb = True
            if 'servingSize' in food_item:
                has_serving_size = True
            if has_protein and has_fat and has_carb and has_serving_size:
                result['Food Name'] = food_item[
                    'lowercaseDescription']
                nutrients = food_item['foodNutrients']
                result['Serving Size'] = f"{food_item['servingSize']}" \
                                      f" {food_item['servingSizeUnit']}"
                result['Protein'] = [f"{nutrient['value']}" \
                                     f" {nutrient['unitName'].lower()}" for
                                     nutrient in nutrients if 'protein' in
                                     nutrient['nutrientName'].lower()][0]
                result['Fat'] = \
                [f"{nutrient['value']} {nutrient['unitName'].lower()}" for
                 nutrient in nutrients if 'fat' in nutrient[
                     'nutrientName'].lower()][0]
                result['Carbs'] = \
                [f"{nutrient['value']} {nutrient['unitName'].lower()}" for
                 nutrient in nutrients if 'carb' in nutrient[
                     'nutrientName'].lower()][0]
                return result
        if len(response_json['foods']) == 0:
            return "try something else"
    return result


def food_from_macros(carbs=0, protein=0, fat=0):
    total_calories = carbs * 4 + protein * 4 + fat * 9
    carb_cals = carbs * 4
    fat_cals = fat * 9
    protein_cals = protein * 4
    if protein_cals / total_calories > .35:
        diet_type = 'high protein'
    elif fat_cals / total_calories > .35:
        diet_type = 'high fat'
    elif carb_cals / total_calories > .65:
        diet_type = 'high carb'
    else:
        # suggest high protein by default
        diet_type = 'high protein'
    top_foods = food_recommendations[diet_type]
    result = {}
    for food in top_foods:
        result[food] = get_food(food)
    return diet_type, result
