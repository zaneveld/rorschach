from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
from random import randint
import urllib
import string
from urllib.request import urlretrieve
import os

def dir_from_location_name(location:str, allowed_special_chars:list = ["_",".","-"]) ->str: 
    """Generate directory name from location name (e.g. "Howling Mines")
    """

    #If there's a location add it next
    f = "_".join(location.split())

    #Filter out any characters that would be a problem in filenames
    f = ''.join(char for char in f if (char.isalnum() or char in allowed_special_chars))

    f = f.lower()

    return f

def filename_from_card_name(card_name:str,location:str="",number:int=1,\
  allowed_special_chars:list = ["_",".","-"], extension:str=".png") ->str:
    """Generate a safe filename from a card name
    card_name = the name of the card
    location = the card location as a string "Cliffs of Howling Winds"
    allowed_special_chars = allowed characters in filename
    number -- suffix for multiple images for each card
    extension -- file extension
    """
    
    #Add card name without whitespace
    f = "_".join(location.split())

    #Add a __ breaker for parsing
    f += "__"

    #If there's a location add it next
    if location:
        f += "_".join(card_name.split())

    #Filter out any characters that would be a problem in filenames
    f = ''.join(char for char in f if (char.isalnum() or char in allowed_special_chars))

    #Add another space
    f += "__"

    #Add final number (if generating multiple portraits per card)
    f += f"{number}"

    f += extension

    f = f.lower()
    return f

def get_prompt(card_name:str,location:str="",card_type:str="",artist:str="",\
  epithet:str="",art_type:str="",card_text:str="",allowed_special_chars ="(). ") -> str:
    """Return an art prompt for card image generation"""
    img_description = f"{card_name}"
    print(img_description)
    
    print(img_description)
    if location:
        img_description += f" in {location}"

    print(img_description)
    if epithet or artist or art_type:
    
        img_description += " ("
    
        if epithet:
            img_description += f"{epithet} "

        if art_type:
            img_description += f"{art_type} "

        if artist:
            img_description += f"{artist}"
    
        img_description += "). "

    print(img_description)

    if card_type and location:
        img_description += f"{card_name} is a type of  {card_type} shown in a place called {location}."
    elif card_type:
        img_description += f"{card_name} is a type of {card_type}. "

    if card_text and epithet and art_type:
        img_description += f"In the {epithet} {art_type} the {card_name} is shown to {card_text}"
    elif card_text:
        img_description += f"The {card_name} is shown to {card_text}" 
    
    print(img_description)
    img_description = img_description.replace("  "," ")
    img_description = img_description.replace("Action","")
    img_description = img_description.strip()
    #Filter out any characters that would be a problem in filenames
    img_description = ''.join(char for char in img_description if (char.isalnum() or char in allowed_special_chars))
    img_description = ' '.join(img_description.split())
    return img_description


def get_location_dir(location,base_dir):
    """Return the directory for a location in base_dir, creating if necessary"""

    #Get the name of the directory with all card images for this location
    location_dir = dir_from_location_name(location)

    #That directory is stored inside the card portrait directory
    location_dir_fp = os.path.join(base_dir,location_dir)

    #If the directory doesn't already exist, create it
    if not os.path.exists(location_dir_fp):
        os.mkdir(location_dir_fp)

    return location_dir_fp
  
def get_card_portrait_image(card_name,location,artist="",epithet="Amazing",\
   card_type="Character",art_type= "Fantasy Card Art",card_portrait_dir = "../images/card_portraits/",max_images=3,\
   card_text = ""):

    location_dir_fp = get_location_dir(location,card_portrait_dir)
  
    img_description = get_prompt(card_name,location=location,artist=artist,\
      epithet=epithet,art_type=art_type,card_type=card_type,card_text=card_text) 
    print("Generating image:",img_description)

    chrome_options = Options()
    #chrome_options.add_argument("--headless")

    driver = webdriver.Chrome('../../dependencies/chromedriver',\
      options=chrome_options)

    #Update to actual web address once 
    #API is working
    driver.get('https://www.crai'+''+'yon.com/')

    prompt = driver.find_element(By.XPATH,'//*[@id="prompt"]')
    time.sleep(randint(5,15))
    prompt.send_keys(img_description)
    draw_button = driver.find_element(By.XPATH,'//*[@id="app"]/div/div/div[1]/button')
    time.sleep(randint(1,3))
    draw_button.click()

    delay_minutes = 3
    for i in range(0,delay_minutes):
        print(f"Waiting....{i+1}/{delay_minutes}") 
        time.sleep(60)
    print("Waiting a few extra seconds for good measure")
    time.sleep(randint(0,30))

    curr_xpath = f'//img[@alt="{img_description}"]'
    
    print("Finding images with XPATH:",curr_xpath)
    output_image_filepaths = []
    images = driver.find_elements(By.XPATH,curr_xpath)
    for i,curr_img in enumerate(images):
        if i >= max_images:
            continue
        print(i,curr_img)
        src = curr_img.get_attribute('src')
        print(src)
        outfile = os.path.join(location_dir_fp,filename_from_card_name(card_name,location,number=i)) 
        print("Saving to outfile:",outfile)
        result = urlretrieve(src, outfile)
        print(result)
        output_image_filepaths.append(outfile)
    return output_image_filepaths


if __name__ == "__main__":
    
    card_filepaths = get_card_portrait_image("Sigil of Sparks (spell)","Mangrove Atoll",artist="")
    print("Generated images:",card_filepaths)
