import base64

# FoodData
fd_api_key = [YOUR FOOD DATA API KEY]

# Kroger
kroger_client_id = [YOUR KROGER CLIENT ID]
kroger_client_secret = [YOUR KROGER CLIENT SECRET]
kroger_encoded_client_info = base64.b64encode(f"{kroger_client_id}"
                                              f":{kroger_client_secret}".encode(
    'ascii')).decode('ascii')

# Spoonacular
# sp_api_key = '&apiKey=c3ca2072fe394799a2e5e6cd19c87fd6'
sp_api_key = [YOUR SPOONACULAR API KEY]
sp_host = 'spoonacular-recipe-food-nutrition-v1.p.rapidapi.com'

