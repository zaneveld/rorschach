#!/usr/bin/env python
# coding: utf-8

import matplotlib
import math
import matplotlib.pyplot as plt
from matplotlib.patheffects import withStroke
import matplotlib.patches as patches
from os.path import join
from os import listdir
from random import choice

def add_text_PIL(original_image,text,x,y,fontsize=30,font_fp=font_fp,color=(0,0,0),outline=4,outline_points=50,    outline_color = (255,255,255),anchor = "la",wrap= True):
    """
    Use the Python Image Library (PIL) to add text to an image
    original_image -- a PIL Image object
    text -- the text to be added to the image, as a string
    x -- the x coordinate for the text
    y -- the y coordinate for the text
    fontsize -- the fontsize of the text
    font_fp -- the path to the location of the font file to be used for the text (e.g. a .ttf file)
    color -- text color in RGB
    outline -- how large of an outline, if any, to draw around the text
    outline_points -- outline is approximated by projecting text in various directions. 
      This parameter controls how many projections are made (e.g. the quality of the outline)
    anchor -- where in the text the x and y coordinates will be anchored. 'la' = left ascender, 'ra' = right ascender
    wrap -- if True, wrap text into multiple lines 
    """   

    font_format = ImageFont.truetype(font_fp,fontsize)
    artist = ImageDraw.Draw(original_image)
    print(type(artist))
    #Have to figure out wrapping before drawing outline (in any)
    if wrap:
        text = ",\n".join(text.split(", "))
        text = ".\n".join(text.split(".  "))  
    
    
    #Draw outline before actual text, so it's behind the text
    
    #This solution is from  Esca Latam on StackOverflow: https://stackoverflow.com/a/61853042/17566480
    if outline: 
        for step in range(0, math.floor(outline * outline_points), 1):
            angle = step * 2 * math.pi / math.floor(outline * outline_points)
            artist.text((x - outline * math.cos(angle), y - outline * math.sin(angle)),               text, outline_color, font=font_format, anchor = anchor)
    
    #Actually draw the text
    image_with_text = artist.text((x,y),text,color,font=font_format, anchor=anchor)
    
      
    
    
    print("Added text:",text," at location ",int(x),int(y))
    return image_with_text


# In[112]:


from PIL import Image, ImageFont, ImageDraw, ImageOps, ImageFilter





def make_game_card(title,card_portrait_fp,card_back="random",attack=None,health=None,\
  cost=1,card_text = "",card_type="",card_back_dir = "../data/card_back_images"):
    #set up image parameters
    width = 825
    height = 1125
    margin = 80
    title_font_size = 40
    portrait_width = int(width - margin * 2)
    portrait_height = int(width - margin * 2)

    left_text_edge = margin
    top_text_edge = margin
    right_text_edge = width - margin
    left_text_edge = margin
    bottom_text_edge = height - margin
    two_thirds_down = height * 4/5

    portrait_location = (int(width/2 - portrait_width/2),int(height/2 - portrait_height/2 - margin))

    if card_back == "random":
        #Load a random card back from card_back_dir
        card_backs = [f for f in listdir(card_back_dir) if f.endswith(".png") or f.endswith(".jpg")]
        #print("Selecting card back from:",card_backs)
        card_back_filename= choice(card_backs)
        #card_back_filename = 'metal_maze.jpg'
        print("Picked card back:",card_back_filename)
        card_template_fp = join(card_back_dir,card_back_filename)
        print("Card template fp:",card_template_fp)

        #Open the card back file
        card_back = Image.open(card_template_fp)
        
    card_image = card_back.copy()

    #Avoid weird rotations after saving due to camera EXIF data
    card_image = ImageOps.exif_transpose(card_image)

    #Scale to card size
    card_image = card_image.resize((width,height))

    #Add outer frame
    artist = ImageDraw.Draw(card_image)
    artist.rectangle([(0,0),(width,height)], fill=None, outline='black',width = int(margin/8))


    #Blur the background
    bluriness = 5
    card_image = card_image.filter(ImageFilter.BoxBlur(5))

    #Paste an even blurrier central image
    card_image_center = card_image.resize((width-margin,height-margin))
    bluriness = 5
    card_image_center = card_image_center.filter(ImageFilter.BoxBlur(20))
    #Paste the card portrait onto the card template
    card_image.paste(card_image_center,(int(margin/2),int(margin/2)))

    if card_portrait_fp:
        #Open the card portrait
        card_portrait = Image.open(card_portrait_fp)
        card_portrait = card_portrait.copy()
        card_portrait = card_portrait.resize((portrait_width,portrait_height))

        #Paste the card portrait onto the card template
        card_image.paste(card_portrait,portrait_location)

    #Add title text
    add_text_PIL(card_image,title,fontsize=title_font_size,x=left_text_edge,y=top_text_edge)

    #Add game text
    add_text_PIL(card_image,card_text, x= left_text_edge, y= portrait_location[1]+portrait_height + int(margin*1/3),fontsize=32)

    if attack is not None:
        #Add power
        power_icon = u"\u2694"
        power_text = u'%i'%attack+power_icon
        add_text_PIL(card_image,power_text,x=left_text_edge,y=bottom_text_edge,fontsize=90,anchor='ld')

    #Add mana cost
    cost_icon = u"\u2748" #sparkle
    cost_text = u"%i"%cost + cost_icon
    cost_txt = add_text_PIL(card_image, cost_text, x=right_text_edge, y= top_text_edge + int(margin*1/4),fontsize=90, anchor = 'rm')

    if health is not None:
        #Add health
        health_icon = u"\u2665" #black heart
        defense_text = u'%i'%health + health_icon
        add_text_PIL(card_image,defense_text,x=right_text_edge,y=bottom_text_edge,fontsize=90,anchor='rd')
        #(rd = right-descender anchor)     

    #Add inner frame
    artist = ImageDraw.Draw(card_image)
    artist.rectangle([(int(margin*1/2),int(margin*1/2)),(int(width-margin*1/2),int(height-margin*1/2))], fill=None, outline='black')

    #Save the result
    output_name = "_".join(title.split()).lower()+".png"
    output_filepath = join(output_folder,output_name)
    print("Card will be saved to ...",output_filepath)

    #Show result
    card_image.show()
    card_image.save(output_filepath,quality = 50,optimize=True)

if __name__ == "__main__":

    card_back_dir = "../data/images/card_backs/"
    output_folder = "../data/images/cards/"
    card_portrait = '../data/images/card_portraits/brave_elf_in_fortress_of_borbyia.png'
    
    # Draw example card using Python Imaging Library

    #system_fonts = matplotlib.font_manager.findSystemFonts() #fontex can be "ttf"
    font_fp = matplotlib.font_manager.fontManager.findfont('DejaVu Sans')

    card_name = "Brave Elf"
    card_type = "Creature — Elf"
    card_text = u"Action — attack an enemy creature.  If there are none, gain 3 \u2694"
    attack = 1
    health = 2
    cost = 1

    make_game_card(card_name,card_portrait_fp=card_portrait_fp, card_back="random",attack=attack,health=health,cost=cost,
      card_text = card_text,card_type= card_type)

