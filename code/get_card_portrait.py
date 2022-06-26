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

def dir_from_location_name(location,allowed_special_chars = ["_",".","-"]):
    """Generate directory name from location name (e.g. "Howling Mines")
    """


    #If there's a location add it next
    f = "_".join(location.split())

    #Filter out any characters that would be a problem in filenames
    f = ''.join(char for char in f if (char.isalnum() or char in allowed_special_chars))

    f = f.lower()

    return f

def filename_from_card_name(card_name,location="",allowed_special_chars = ["_",".","-"],number="1",extension=".png"):
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
    f += f"__{number}"

    f += extension

    f = f.lower()
    return f

def get_card_portrait_image(card_name,location,artist="N.C. Wyeth",epithet="Amazing", art_type= "Fantasy Card Art"):

    img_description = f"{card_name} in {location} ({epithet} {art_type}"
    if artist:
        img_description += f" by {artist}"
    img_description += ")"
    
    print("Generating image:",img_description)

    chrome_options = Options()
    #chrome_options.add_argument("--headless")

    driver = webdriver.Chrome('../../dependencies/chromedriver',\
      options=chrome_options)

    #Update to actual web address once 
    #API is working
    driver.get('https://www.crai'+''+'yon.com/')

    prompt = driver.find_element(By.XPATH,'//*[@id="prompt"]')
    print("Prompt WebElement:",prompt)
    time.sleep(randint(5,15))
    prompt.send_keys(img_description)
    draw_button = driver.find_element(By.XPATH,'//*[@id="app"]/div/div/div[1]/button')
    print("Draw button WebElement:",draw_button)
    time.sleep(randint(1,3))
    draw_button.click()

    delay_minutes = 3
    for i in range(0,delay_minutes):
        print(f"Waiting....{i}/{delay_minutes}") 
        time.sleep(60)
    print("Waiting a few extra seconds for good measure")
    time.sleep(randint(0,30))

    curr_xpath = f'//img[@alt="{img_description}"]'
    
    print("Finding images with XPATH:",curr_xpath)
    output_image_filepaths = []
    images = driver.find_elements(By.XPATH,curr_xpath)
    for i,curr_img in enumerate(images):
        print(i,curr_img)
        src = curr_img.get_attribute('src')
        print(src)
        outfile = filename_from_card_name(card_name,location,number=i) 
        print("Saving to outfile:",outfile)
        result = urlretrieve(src, f"../data/images/card_portraits/{outfile}")
        print(result)
        output_image_filepaths.append(outfile)
    return output_image_filepaths


if __name__ == "__main__":
    
    card_filepaths = get_card_portrait_image("Sigil of Sparks (spell)","Mangrove Atoll",artist="")
    print("Generated images:",card_filepaths)
