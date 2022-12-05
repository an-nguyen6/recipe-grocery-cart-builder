import base64

# FoodData
fd_api_key = 'JOS7wARkFRFc9bk9d94bEqpg8hPR7vPSM3Lk123l'

# Kroger
kroger_client_id = 'intermediatepythonproject-32fd2ef3198aa79125db1f467993a7d42156649754783938330'
kroger_client_secret = 'ctdQmwXXumi4CHSFsV0ZjUejV9FGnEXpcO4IhtwW'
kroger_encoded_client_info = base64.b64encode(f"{kroger_client_id}"
                                              f":{kroger_client_secret}".encode(
    'ascii')).decode('ascii')

# Spoonacular
# sp_api_key = '&apiKey=c3ca2072fe394799a2e5e6cd19c87fd6'
sp_api_key = '72efea0b89msh2c33c33410c53c7p125632jsne38436fd9c93'
sp_host = 'spoonacular-recipe-food-nutrition-v1.p.rapidapi.com'

