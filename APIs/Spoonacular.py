import requests
from APIs import config

api_key = config.sp_api_key
api_host = config.sp_host

# search recipes by ingredients from user input (return up to 5)
def get_recipe_from_ingredients(ingredient_list: list):
	base_url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes"
	search_type = 'findByIngredients'
	querystring = {"ingredients": f"{ingredient_list}", "number": "5",
				   "ignorePantry": "true", "ranking": "1"}
	headers = {
		"X-RapidAPI-Key": api_key,
		"X-RapidAPI-Host": api_host
	}
	url = f"{base_url}/{search_type}"
	response = requests.request("GET", url, headers=headers, params=querystring)
	result = {}
	response_json = response.json()
	for recipe in response_json:
		result[recipe['title']] = {}
		result[recipe['title']]['Missing Ingredients'] = []
		for item in recipe['missedIngredients']:
			result[recipe['title']]['Missing Ingredients'].append(f""\
											f"{item['amount']} {item['unit']} {item['name']}")
	if len(result) == 0:
		result = {"None": {"No result":"try something else"}}
	return result


# search recipes by macros (return up to 5)
def get_recipes_from_macros(carbs=0, protein=0, fat=0):
	base_url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes"
	search_type = 'findByNutrients'
	querystring = {"minProtein": f"{protein}", "minCarbs": f"{carbs}",
				   "minFat": f"{fat}",
				   "number": "5"}
	headers = {
		"X-RapidAPI-Key": api_key,
		"X-RapidAPI-Host": api_host
	}
	url = f"{base_url}/{search_type}"
	response = requests.request("GET", url, headers=headers, params=querystring)
	response_json = response.json()
	result = {}

	for recipe in response_json:
		result[recipe['title']] = {}
		result[recipe['title']]['Calories'] = recipe['calories']
		result[recipe['title']]['Protein'] = recipe['protein']
		result[recipe['title']]['Fat'] = recipe['fat']
		result[recipe['title']]['Carbs'] = recipe['carbs']
		search_type_search_recipe = f"{recipe['id']}/information"
		url_search_recipe = f"{base_url}/{search_type_search_recipe}"
		response_search_recipe = requests.request("GET", url_search_recipe,
												  headers=headers)
		recipe_details = response_search_recipe.json()
		result[recipe['title']]['Source'] = recipe_details['sourceUrl']
		ingredients = []
		for ingredient in recipe_details['extendedIngredients']:
			ingredients.append(ingredient['original'])
		result[recipe['title']]['Ingredients'] = ingredients

	return result
