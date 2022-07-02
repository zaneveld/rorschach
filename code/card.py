from random import shuffle,choice
from collections import deque,defaultdict
import pandas as pd
import  ast
from rorschach.code.make_card_image import make_game_card
from rorschach.code.get_card_portrait import dir_from_location_name,filename_from_card_name,\
  get_location_dir
import os
from os import listdir
from rorschach.code.effect import EffectSet,Effect,DealDamage,Draw,GainManaCrystals,Heal,DiscardRandom
from rorschach.code.player import Player

class CardSet(object):
    """Represents a set of cards
    """        
    def __init__(self,set_data_fp,effect_library):
        """A CardSet represents the set of cards that can be in the game

        set_data_fp: the path to the .tsv text file holding card data
        effect_library: reference to an EffectSet object defining game effects
        """
        self.EffectLibrary = effect_library
        card_data = pd.read_csv(set_data_fp,sep="\t")
        card_data.dropna(axis=0,how="all", inplace=True) 
        card_data.dropna(axis=1,how="all", inplace=True) 
        cards_to_make = list(card_data["card_name"])
        card_data.set_index("card_name",inplace=True,drop=False)
        self.CardData = card_data
        self.Cards = self.makeCards(cards_to_make) 

    def makeCards(self,card_names,copies=1):
        """Generate cards of a given type
        card_names: a list of the names of the cards to make
        copies: the number of copies of each card to make 
        """

        #It is the responsibility of each card
        #maker to colllect any information needed
        #from a dict representing the textual data in the
        #data sheet.

        cards = []
        for card_name in card_names:
            for i in range(copies):
                curr_card = self.makeCard(card_name)
                cards.append(curr_card)
        return cards

    def makeCard(self,card_name):
        """Generate a card of the given type"""

        card_makers = {"Creature":Creature,"Spell":Spell}

        card_supertype = self.CardData.loc[card_name,"supertype"]

        card_as_dict = self.CardData.loc[card_name,:].to_dict()

        ##drop empty values:
        card_as_dict = {k:v for k,v in card_as_dict.items() if (v and not pd.isna(v))}
        card_as_dict["effect_library"]=self.EffectLibrary

        #Make the card with the appropriate class for its supertype
        print("ABOUT TO MAKE CARD:",card_as_dict)
        card = card_makers[card_supertype](**card_as_dict)
        return card 
 
class Card(object):
    """Superclass for Spells and Creatures"""
    
    def setUpEffects(self,effect_text,effect_library,numeric_params=["magnitude"]):
        """Set up effects
        """
        self.Effects = []
        self.EffectLibrary = effect_library
        
        if not effect_text:
            return False
        print(f"Setting up effects: {effect_text}")
        
        #Effect text should be a dict of effect name: magnitude
        effect_dict = ast.literal_eval(effect_text)
        for effect_name,effect_params in effect_dict.items():
            #effect params are passed on to makeEffect as a kwargs
            #convert numeric params to ints
            for p in numeric_params:
                if p in effect_params:
                    effect_params[p] = int(effect_params[p])
            effect = effect_library.makeEffect(effect_name,**effect_params)
            self.Effects.append(effect)
        return True
 
    def getTargets(self):
        """Get targets for each effect in the card ability, return False if missing targets"""
        required_targets_assigned = True
        for effect in self.Effects:
            for target_type,n_targets in effect.RequiredTargets.items():
                print("Looking for target of type:",target_type," x",n_targets)        
                effect.Targets = []                
                if target_type == "random enemy minion":
                    targets = self.Controller.getRandomEnemyMinions(n=n_targets)                
                elif target_type == "all minions":
                    targets = self.Controller.getAllMinions()
                elif target_type == "all enemy minions":
                    targets = self.Controller.getAllEnemyMinions()                
                elif target_type == "random friendly minion":
                    targets = self.Controller.getRandomFriendlyMinions(n=n_targets)                
                elif target_type == "random friendly damaged minions":
                    targets = self.Controller.getRandomFriendlyDamagedMinions(n=n_targets)
                elif target_type == "controller":
                    targets = [effect.Controller]
                elif target_type == "opponent":
                    targets = [effect.Controller.Opponent]
                elif target_type == "all players":
                    targets = [effect.Controller,effect.Controller.Opponent]
                else:
                    raise NotImplementedError(f"Target type {target_type} is not recognized")
                effect.Targets = targets
                if not targets:
                    required_targets_assigned = False
        return required_targets_assigned
       

    def makeCardImage(self,card_back_filename="random",text="",power=None,toughness=None):
        cost = self.Cost  
        if self.Types:
            card_type = " and ".join(self.Types) 
        else:
            card_type = self.CardType

        card_name = self.Name
        card_image_dir = get_location_dir(self.Location,\
          base_dir = "../data/images/cards")
        card_filename = filename_from_card_name(self.Name,self.Location)

        if card_filename not in listdir(card_image_dir):
            card_image_fp = make_game_card(card_name,\
              location = self.Location,\
              card_portrait_filename="generate",\
              card_back_filename=card_back_filename,\
              attack=power,health=toughness,\
              cost=cost,card_text = text,card_type=card_type)
        else:
            card_image_fp = os.path.join(card_image_dir,card_filename)
        return card_image_fp

    def activate(self):
        """Resolve the effects of the card's activated ability"""
        for i,effect in enumerate(self.Effects):
            effect.activate()
    
    def setController(self,controller):
        """Set the controller of this Spell and its effects"""
        self.Controller = controller
        for effect in self.Effects:
            effect.Controller = self.Controller
 

class Spell(Card):
    def __init__(self,card_name,mana_cost,effects,effect_library,\
      location="",behavior="Temporary Effect",controller = None,types=[],supertype="Spell",portrait_fp=None,\
      card_back_filename="random"):
        """A spell 
        card_name -- the name of the card
        mana_cost -- the mana cost of the spell (integer)
        effects -- a list of Effect objects
        """
        self.Name = card_name
        self.Cost = mana_cost
        self.CardType = "Spell"
        self.Types = types
        self.Behavior = behavior
        self.setUpEffects(effects,effect_library)
        self.setController(controller)
        self.Portrait = portrait_fp
        self.Location = location
        print("Current Location:",location)
        self.CardBackFilename = card_back_filename
        if self.Effects:
            card_text = ", ".join([str(effect) for effect in self.Effects])
        else:
            card_text = ""
        self.CardImageFilepath = self.makeCardImage(self.CardBackFilename,text=card_text)
    
    def __repr__(self):
        effects = self.Effects
        if effects:
            effects = ",".join([str(effect) for effect in self.Effects])
        else:
            effects = ""
        return f"{self.Name}({self.Cost}):{effects}"
  

class Creature(Card):
    def __init__(self,card_name,effect_library,mana_cost=0,location="",\
        power=0,toughness=0,\
        effects="{}",supertypes="",controller=None,static_abilities="",\
        behavior="Attack Random Enemy",supertype="Creature",types="",portrait_fp=None,card_back_filename="random"):
        """Make a new creature card
        """
        self.Name = card_name
        self.Power = int(power)
        self.Toughness = int(toughness)
        self.Controller = controller
        self.Cost = int(mana_cost)
        self.CardType = supertype
        self.Behavior = behavior
        self.Location = location
        self.CurrentHealth = self.Toughness
        self.Dead = False
        self.StaticAbilities = static_abilities.split(",")
        self.BaseStaticAbilties = self.StaticAbilities
        self.SuperTypes = supertypes.split(",") 
        self.SuperTypes.append(supertype)
        self.Types = types.split(",")
        self.setUpEffects(effects,effect_library)
        self.setController(controller)
        self.Portrait = portrait_fp
        print("Current Location:",location)
        self.CardBackFilename = card_back_filename
        card_text = "Action — "+self.Behavior + "\n" + ", ".join([str(effect) for effect in self.Effects]) +"\n " + ", ".join(self.StaticAbilities)
        self.CardImageFilepath = self.makeCardImage(card_back_filename,text=card_text)

    def __repr__(self):
        if self.checkIfDead():
            return f"{self.Name} (Dead)"
        return f"{self.Name}({self.Cost}):{self.Power}/{self.CurrentHealth}"
 
    def attack(self,target):
        """Resolve an attack"""

        print(f"{self.Name} attacks {target.Name} for {self.Power} damage")        
        damage_dealt = self.dealDamage(target,self.Power)
        print(f"After all abilities are resolved, {target.Name} takes {damage_dealt} damage")
        
        #Ranged creatures only suffer damage when defending,
        #and only deal damage when attacking
        if "Creature" in target.SuperTypes and\
            "Ranged" not in target.StaticAbilities and\
            "Ranged" not in self.StaticAbilities:
            print(f"{self.Name} takes {target.Power} damage during its attack")
            target.dealDamage(target=self,amount=target.Power)
        elif "Ranged" in self.StaticAbilities:
            print(f"{target.Name} doesn't get a chance to attack back because {self.Name} is Ranged")
 
        if "Parasitic" in self.StaticAbilities:
            print(f"{self.Name} parasitises {target.Name} for {damage_dealt} Health")            
            self.healDamage(damage_dealt)
 
    def canAttack(self,target):
        """Return True if it is possible, in general, to attack target"""

        if "Player" in target.SuperTypes:
            print(f"{target.Name} is a player, so {self.Name} can attack it")
            return True

        if "Creature" not in target.CardType:
            print(f"{target.Name} is not a player or creature, so {self.Name} can't attack it")
            return False
        
        if "Flying" in target.StaticAbilities\
          and "Flying" not in self.StaticAbilities\
            and "Ranged" not in self.StaticAbilities:
            print(f"{target.Name} is Flying, but {self.Name} doesn't have Flying or Ranged, so {self.Name} can't attack it")
            return False
       
        print(f"No special rules apply, {self.Name} can attack {target.Name}") 
        return True
 
    def dealDamage(self,target,amount=1,damage_type="physical"):
        """Deal a certain amount of damage to a target"""
        #If the target has a special ability,
        #the amount of actual damage dealt may not
        #be the nominal amount
        damage_dealt = target.takeDamage(amount,damage_type)
        return damage_dealt

    def takeDamage(self,amount=1,damage_type="physical"):
        """Take a certain amount of damage"""
        self.CurrentHealth -= amount
        damage_taken = amount
        self.CurrentHealth = max(0,self.CurrentHealth)
        if self.checkIfDead():
            self.die()
        return damage_taken

    def healDamage(self,amount=1):
        """Heal a certain amount of damage"""
        self.CurrentHealth += amount
        self.CurrentHealth = min(self.CurrentHealth,self.Toughness)
 
    def die(self):
        """Remove the creature"""
        self.Dead = True
        print(f"{self.Name} dies")
        for i,creature in enumerate(self.Controller.Board):
                if creature == self:
                    self.Controller.Board.pop(i)
                    break #don't kill later copies
    
    def isDamaged(self):
        """Return True if the creature is currently damaged"""
        if self.CurrentHealth < self.Toughness:
            return True
        else:
            return False

    def hasAbility(self,ability):
        """Return True if the creature has a specified static ability"""
        if ability in self.StaticAbilities:
            return True
        else:
            return False

    def hasType(self,creature_type):
        """Return True if the creature has a specific creature type"""
        if creature_type in self.Types:
            return True
        else:
            return False            
 
    def checkIfDead(self):    
        """Return True if dead"""        
        if self.Dead or self.CurrentHealth == 0:
            return True
        else: 
            return False

