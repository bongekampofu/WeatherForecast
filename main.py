import requests
import json
from flask import Flask

#sign up at https://api.weatherapi.com and get the api key
API = "06ccb275663d4297982145820241902"
#include air quality index
aqi="yes"



city_name = input("Enter city name to gets its weather information. ")
url = f"http://api.weatherapi.com/v1/current.json?key={API}&q={city_name}&aqi={aqi}" 
result = requests.get(url)  # Will call the website and fetch information
#successful response code is 200
print(result)
#data is more readable with json module
wdata = json.loads(result.text)  
print(wdata)

name = wdata["location"]["name"]

