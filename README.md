# FastMCP-V1
## Technology:
## Purpose:
The purpose of this project is to be able to find resturants through LLM that are within a mile radius. When people look for food to eat at you usually factor in price. the user can then prompt the llm host of the budget and the output will be a list of resturants which will be saved to a database. The search results will be reused for 60 days. after that it will rerun the search. a menu parser will be ran for each resurtant and data will be saved to a databse. The results will also be good and reused for 60 days. after then a parser will then need to be ran. 

## Problem:
use LLM to find something to eat produces very limited results instead of seeming the options and possible combinations that is within someeones budget.

## Built with 
fast MPC
Pyhton

## SetUp
include an .env file which contains keys for api and usernames and passwords for connection to your account.

Mongo DB:
MONGO_URI: **ENTER IN YOUR URL**

gmail:
EMAIL_ADDRESS: **Enter IN YOUR EMAIL ADDRESS**
EMAIL_PASSWORD: **ENTER IN YOUR EMAIL PASSWORD**

google maps api key:

##