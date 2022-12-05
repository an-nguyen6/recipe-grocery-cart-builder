## Recipe and Grocery Cart Builder
A wep app to help users plan meals around macros and foods of their liking. 
Users can also log in to their Kroger account and look up product 
availability at a local Kroger chain (e.g. Mariano's if you're in the 
Chicagoland area) and add products to their cart. 

## Getting Started
- To fully use this app, register for a Kroger account
- Ensure you have pipenv installed `pip install pipenv`
- Create pipenv environment `pipenv install`
- Install hypercorn within your pipenv environment `pipenv install hypercorn`
- Initiate the pipenv environment and run using hypercorn `pipenv shell` then 
  `hypercorn main:app --reload`

## To implement
- Register for the FoodData API and get your API key
- Register for the Spoonacular API and get your API key and host
- Register for the Kroger API and get your client ID and secret

## Project proposals
Project idea #1: Create an API to help people plan meals and buy groceries to meet their nutrition goals. 
Things to implement:
1. Take someone’s macronutrient preferences and using a nutrition facts API 
(FoodData Central) suggest some foods to start
2. Based on someone’s inputs on basic food/ingredients they’d like to eat, 
  it’ll return recipe suggestions (Spoonacular API)
3. Based off recipes or food selections, it will call a grocery API (e.g. 
  Kroger, Instacart) to check for food item availability 
4. It may also add items to cart in Instacart using their API 
5. Wrap all this up in a web app for users to access

Implementation Timeline

1. Week 5: Confirm access to necessary API's and datasets, one of the 
   following or something similar (FoodData Central, Spoonacular, Kroger or Instacart)
2. Week 6: Have a basic data model to represent food suggestions and recipes.
   Begin building recommendation algorithm for food and recipes. 
3. Week 7: Wrap up recommendation algorithm. Implement grocery availability 
   and ordering calls. Explore web app frameworks.
4. Week 8: Implement and finalize web app for end user.
5. Week 9: Final touches and submit project