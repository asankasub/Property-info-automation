#Importing relevant libraries.

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
import json
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

#Preparing chrome driver.

chrome_driver_path = "C:/Users/Asanka/Desktop/chromedriver"
driver = webdriver.Chrome(service=Service(chrome_driver_path))

#Address of form that needs to be filled out for each property.

form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdeyHXPHynq55yiGSPbFo-O-_HGTJI3Vnr0R6-4Egwais4C7A/viewform?usp=sf_link"

#Calling environment variables.

load_dotenv("C:/Users/Asanka\Desktop/Python Practice/Data-entry-automation/env (1)")

#Passing through user-agent and accept-language to zillow link.

WEBSITE = os.environ.get("WEBSITE")
HEADERS = {
    "User-Agent": os.environ.get("USER_AGENT"),
    "Accept-Language": os.environ.get("ACCEPT_LANGUAGE")
}

response = requests.get(url=WEBSITE, headers=HEADERS)

#Scraping zillow url for relevant data and passing it into a python dictionary by using Beautiful Soup.

#Calling zillo page.

zillo_page = response.text

#Getting html of page with Beautiful Soup
soup = BeautifulSoup(zillo_page, "lxml")

#Scraping specific tag that contains all relevant information.

script_data = soup.select_one("script[data-zrr-shared-data-key]").contents[0].strip("!<>\-")

#At this point I created a json file to view the entire content of the script tag. 
data = json.loads(script_data)  

with open('data.json','w') as f:
    json.dump(data,f, indent=4)

#Viewing the json file with a json viewer in order to locate property
#information and storing it in a variable called property_info.

property_info = data["cat1"]["searchResults"]["listResults"]

#Searching address, price, and link information of properties and storing it in relevant lists.

address, price, link = [],[],[]

for item in property_info:

    address.append(item["address"])

    #Some properties were missing a units key in property_info which is supposed to contain property prices. These properties had an unformatted price key instead. 
    # Depending on the situation, the price is appended to the property price list.

    price.append(item["units"][0]["price"].strip("$+").replace(",", "") if 'units' in item else item["unformattedPrice"])

    #Some urls in the detail url key of each property were missing the beginning of the url. For these situations, the beginning of the 
    #url would be attached to the rest of the url, and the final product would be appended to the property link list.

    link.append(item["detailUrl"] if item["detailUrl"].startswith("http") else f"https://www.zillow.com{item['detailUrl']}")

#Using the chrome driver now with selenium to access the property form.

driver.get(form_url)

time.sleep(3)

# This loop fills out a form for each property. 

for i in range(len(address)):

    #Each question entry spot is located, and the relevant information is provided.
    #The questions ask for the location, price, and link of each property respectively.

    first_question = driver.find_element(By.XPATH,"//*[@id='mG61Hd']/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div/div[1]/input")
    first_question.send_keys(address[i])
 
    sec_question = driver.find_element(By.XPATH,"//*[@id='mG61Hd']/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input")
    sec_question.send_keys(f"$ {price[i]}")
   
    third_question = driver.find_element(By.XPATH, "//*[@id='mG61Hd']/div[2]/div/div[2]/div[3]/div/div/div[2]/div/div[1]/div/div[1]/input")
    third_question.send_keys(link[i])

    #The submit button is then located and clicked.

    submit_button = driver.find_element(By.XPATH, "//*[@id='mG61Hd']/div[2]/div/div[3]/div[1]/div[1]/div/span/span")
    submit_button.click()
  
    #After the submit button is clicked, the new form button is located and clicked.

    new_form = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[1]/div/div[4]/a")
    new_form.click()
    




