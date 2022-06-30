#!/usr/bin/env python
# coding: utf-8
import os
import matplotlib
import math
import matplotlib.pyplot as plt
from matplotlib.patheffects import withStroke
import matplotlib.patches as patches
from os.path import join
from os import listdir
from random import choice
from PIL import Image, ImageFont, ImageDraw, ImageOps,\
   ImageFilter,ImageEnhance

from get_card_portrait import filename_from_card_name,dir_from_location_name,get_location_dir,get_card_portrait_image
import textwrap

def add_text_PIL(original_image,text,x,y,fontsize=30,font_fp=None,color=(0,0,0),outline=4,outline_points=50,    outline_color = (255,255,255),anchor = "la",wrap= True,max_chars_per_line:int=40):
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
    max_chars_per_line -- maximum number of characters on each line

    """   
    if not font_fp:
        font_fp = matplotlib.font_manager.fontManager.findfont('DejaVu Sans')

    font_format = ImageFont.truetype(font_fp,fontsize)
    artist = ImageDraw.Draw(original_image)
    print(type(artist))
    #Have to figure out wrapping before drawing outline (in any)
    if wrap:
        text = ",\n".join(text.split(", "))
        text = ".\n".join(text.split(".  "))  
        lines = text.splitlines()
        text = "\n".join([textwrap.fill(l,max_chars_per_line) for l in lines])
    
    #TODO: really neat trick for getting pixel size of text to incorporate
    #https://stackoverflow.com/questions/43730389/correctly-centring-text-pil-pillow
    
    #Draw outline before actual text, so it's behind the text
    #This solution is from  Esca Latam on StackOverflow: https://stackoverflow.com/a/61853042/17566480
    if outline: 
        for step in range(0, math.floor(outline * outline_points), 1):
            angle = step * 2 * math.pi / math.floor(outline * outline_points)
            artist.text((x - outline * math.cos(angle), y - outline * math.sin(angle)),\
              text, outline_color, font=font_format, anchor = anchor)
    
    #Actually draw the text
    image_with_text = artist.text((x,y),text,color,font=font_format, anchor=anchor)
   
    return image_with_text


def make_game_card(title:str,location:str,attack:int=None,health:int=None,cost:int=1,\
  card_text:str = "",card_type:str="",card_portrait_filename:str="generate",card_back_filename:str="random",\
  base_card_portrait_dir:str="../data/images/card_portraits/",card_back_dir:str = "../data/images/card_backgrounds",
  output_dir:str="../data/images/cards/") -> str:
    """Make a game card image by superimposing a cardback image with a generated portrait and text

    Returns: location of generated image file
    """
    #set up image parameters
    width = 825
    height = 1125
    
    margin = 80
    box_indent = int(margin*1/2)
    
    title_font_size = 40
    max_title_chars = 25
    #if len(title) > max_title_chars:
    #    title_font_size -= 3
    
    portrait_width = int(width - margin * 2)
    portrait_height = int(width - margin * 2)

    left_text_edge = margin
    top_text_edge = margin
    right_text_edge = width - margin
    left_text_edge = margin
    bottom_text_edge = height - int(margin/2)
    two_thirds_down = height * 4/5

    portrait_location = (int(width/2 - portrait_width/2),\
      int(height/2 - portrait_height/2 - margin))
    
    text_box_location = (int(width/2 - portrait_width/2)-box_indent,\
      int(height/2 + portrait_height/2 - box_indent*3))

    card_text_height = portrait_location[1]+portrait_height + int(margin*1/3)

    card_backs = [f for f in listdir(card_back_dir) if f.endswith(".png") or f.endswith(".jpg")]
    
    if card_back_filename == "random":
        #Load a random card back from card_back_dir
        card_back_filename= choice(card_backs)
        print("Picked card back:",card_back_filename)
    elif card_back_filename not in card_backs:
        raise ValueError(f"Couldn't find card back {card_back}. Valid option are: {card_backs}")

    card_back_fp = join(card_back_dir,card_back_filename)

    #Open the card back file
    card_back = Image.open(card_back_fp)
        
    card_image = card_back.copy()

    #Avoid weird rotations after saving due to camera EXIF data
    card_image = ImageOps.exif_transpose(card_image)

    #Scale to card size
    card_image = card_image.resize((width,height))

    #Add outer frame
    artist = ImageDraw.Draw(card_image)
    artist.rectangle([(0,0),(width,height)], fill=None,\
      outline='black',width = int(margin/8))

    #Blur the background
    bluriness = 5
    card_image = card_image.filter(ImageFilter.BoxBlur(5))

    #Paste an even blurrier central image
    card_image_center = card_image.resize((width-margin,height-margin))
    bluriness = 5
    card_image_center = card_image_center.filter(ImageFilter.BoxBlur(20))
    #Paste the card portrait onto the card template
    card_image.paste(card_image_center,(int(margin/2),int(margin/2)))

    
    #If a location was passed, the code assumes portraits will be stored
    #in a subfolder for that location e.g. ../data/images/card_portraits/the_swamp_of_madness/    
    if location:
        card_portrait_dir = get_location_dir(location,base_dir=base_card_portrait_dir)
    else:
        card_portrait_dir = base_card_portrait_dir

    
    if card_portrait_filename == "generate":
        card_portrait_filename = filename_from_card_name(card_name=title,location=location,number=1,extension=".png")
        card_portrait_fp = join(card_portrait_dir,card_portrait_filename)
        if os.path.isfile(card_portrait_fp):
            #Card portrait must already have been generated
            pass
        else:
            #Generate a new card image!
            #Note that get_card_portrait image will generate
            #a directory based on location
            
            #So we just pass in the base directory
            card_portrait_images = get_card_portrait_image(title,location,
              card_type=card_type,card_portrait_dir=base_card_portrait_dir)
            
            card_portrait_fp = choice(card_portrait_images)
    
    elif card_portrait_filename:
        card_portrait_fp = join(card_portrait_dir,card_portrait_filename)
    
    #Open the card portrait
    card_portrait = Image.open(card_portrait_fp)
    card_portrait = card_portrait.copy()
    card_portrait = card_portrait.resize((portrait_width,portrait_height))

    #Paste the card portrait onto the card template
    card_image.paste(card_portrait,portrait_location)

    #Set up title box
    card_title_box = card_image_center.copy()

    #Paste an even blurrier central image
    card_title_box =\
      card_title_box.resize((portrait_width+box_indent*2,margin*2))

    #reduce contrast in type box
    contrast_enhancer = ImageEnhance.Contrast(card_title_box)
    card_title_box = contrast_enhancer.enhance(0.3)

    #reduce color in type box 
    color_enhancer = ImageEnhance.Color(card_title_box)
    card_title_box = color_enhancer.enhance(0.8)

    #brighten type box a lot so it's readable
    enhancer = ImageEnhance.Brightness(card_title_box)
    card_title_box = enhancer.enhance(1.8)

    #Paste the card type box onto the card template
    card_image.paste(card_title_box,(left_text_edge - box_indent,\
      top_text_edge - box_indent))

    #Add title text
    add_text_PIL(card_image,title,fontsize=title_font_size,x=left_text_edge,\
      y=top_text_edge,wrap=True,max_chars_per_line = max_title_chars)
    
    #Set up text box 
    box_indent = int(margin*1/2)
    text_box_image = card_image_center.copy()
    text_box_image = \
      text_box_image.resize((width - box_indent*2,margin*3+box_indent+\
      int(box_indent*1/8)))

    #brighten text box a lot so it's readable
    brightness_enhancer = ImageEnhance.Brightness(text_box_image)    
    text_box_image = brightness_enhancer.enhance(2.5)

    #reduce saturation
    saturation_enhancer = ImageEnhance.Color(text_box_image)
    text_box_image = saturation_enhancer.enhance(0.8)

    #reduce contrast
    contrast_enhancer = ImageEnhance.Contrast(text_box_image)
    text_box_image = contrast_enhancer.enhance(0.3)
    
    #Actually draw the text box onto the card image
    card_image.paste(text_box_image,text_box_location)
    
    #Add game text
    add_text_PIL(card_image,card_text, x= left_text_edge,\
      y= card_text_height,fontsize=28)
    
    if card_type:
        
        #Add card type box
        card_type_box = card_image_center.copy()    
        
        #Paste an even blurrier central image
        card_type_box =\
          card_type_box.resize((portrait_width-box_indent*2,margin))

        #reduce contrast in type box
        contrast_enhancer = ImageEnhance.Contrast(card_type_box)
        card_type_box = contrast_enhancer.enhance(0.8)
       
        #reduce color in type box 
        color_enhancer = ImageEnhance.Color(card_type_box)
        card_type_box = color_enhancer.enhance(0.8)
 
        #brighten type box a lot so it's readable
        enhancer = ImageEnhance.Brightness(card_type_box)    
        card_type_box = enhancer.enhance(1.8)
        
        #Paste the card type box onto the card template
        card_image.paste(card_type_box,(margin+box_indent,\
          card_text_height - int(margin)-int(margin*1/8)))
        
        #Add card type text
        add_text_PIL(card_image,card_type, x=int(width/2),\
          y= card_text_height - int(margin*1/3),fontsize=38,anchor='md')

    if attack is not None:
        #Add power
        power_icon = u"\u2694"
        power_text = u'%i'%attack+power_icon
        add_text_PIL(card_image,power_text,x=left_text_edge,y=bottom_text_edge,fontsize=90,anchor='ld')

    #Add mana cost
    cost_icon = u"\u2748" #sparkle
    cost_text = u"%i"%cost + cost_icon
    cost_txt = add_text_PIL(card_image, cost_text, x=right_text_edge,\
      y= top_text_edge,fontsize=90, anchor = 'ra')

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
    if location:
        output_dir = get_location_dir(location,base_dir=output_dir)
    
    output_filename = filename_from_card_name(card_name=title,\
      location=location,number=1,extension=".png") 
    
    output_filepath = join(output_dir,output_filename)
    print("Card will be saved to ...",output_dir)

    #Show result
    #card_image.show()
    card_image.save(output_filepath,quality = 50,optimize=True)
    return output_filename

if __name__ == "__main__":

    card_back_dir = "../data/images/card_backs/"
    output_folder = "../data/images/cards/"
    
    # Draw example card using Python Imaging Library
    #card_name = "Persecuted Orc"
    #card_type = "Creature — Orc"
    #card_text = u"Action — Defend.  Trigger - When this leaves play, damage a creature 1"
    #cost = 1
    #attack = 2
    #health = 1
    #location = "Blessed Temple of Mushrooms"
    #card_back_filename = "card_back_Decay-01.png"
    
    card_name = "Basalto's Unutterable Ululation"
    card_type = "Spell — Enchantment"
    card_text = u"Trigger - When you take damage, deal 5 sonic damage to a random creature"
    cost = 6
    attack = None
    health = None
    location = "Blessed Temple of Mushrooms"
    #card_back_filename = "card_back_Decay-01.png"
    card_back_filename = "random"

    make_game_card(card_name,location = location, card_portrait_filename="generate", card_back_filename=card_back_filename,\
      attack=attack,health=health,cost=cost,card_text = card_text,card_type= card_type)

