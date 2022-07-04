from random import shuffle,choice
from collections import deque,defaultdict
import pandas as pd
import  ast
from rorschach.code.make_card_image import make_game_card
from rorschach.code.get_card_portrait import dir_from_location_name,filename_from_card_name,\
  get_location_dir
import os
from os import listdir

class EffectSet(object):
    """Represents the set of effects in the game
    """
    def __init__(self,set_data_fp):
        """A CardSet represents the set of cards that can be in the game

        set_data_fp: the path to the .tsv text file holding effect data
        """
        
        effect_data = pd.read_csv(set_data_fp,sep="\t")
        effect_data.dropna(axis=0,how="all", inplace=True) 
        effect_data.dropna(axis=1,how="all", inplace=True) 
        effects_to_make = list(effect_data["effect_name"])
        effect_data.set_index("effect_name",inplace=True,drop=False)
        self.EffectData = effect_data
        
        #References to actual objects that handle each type of effect
        self.EffectMakers =\
          {\
            "deal damage":DealDamage,
            "gain mana crystals":GainManaCrystals,
            "heal":Heal,
            "draw":Draw,
            "discard random":DiscardRandom,
            "resurrect random":ResurrectRandomCreatures
          }
    
        self.Effects = self.makeEffects(effects_to_make) 
    
    def makeEffects(self,effect_names):
        """Generate effects of a given type
        effect_names: a list of the effects of the cards to make
        """
        effects = []
        for effect_name in effect_names:
            effect = self.makeEffect(effect_name)
            effects.append(effect)
        return effects

    def makeEffect(self,effect_name,**kwargs):
        """Generate an effect
        effect name - base name of the effect (may include {X} placeholders)
        magnitude - the size of the effect (replaces {X})
        """
        effect_as_dict = self.EffectData.loc[effect_name,:].to_dict()

        ##drop empty values:
        effect_as_dict = {k:v for k,v in effect_as_dict.items() if (v and not pd.isna(v))}
        effect_as_dict.update(kwargs)
        print("Updated effect as dict:", effect_as_dict)
 
        effect_type = effect_as_dict["effect_type"]
        effect_maker = self.EffectMakers[effect_type]
        
        effect = effect_maker(**effect_as_dict)
        return effect           

class Effect(object):
    def __init__(self,effect_name,conditions=None,targets=None,controller=None,magnitude=1,required_target_types=None,effect_type=None,damage_type="physical",narrative_description=""):
        """Represent a game effect
        effect_name: a string representing the unique name of the effect
        conditions: a string representing conditions on the effect
        targets: actual targets of the specific effect (references to e.g. Creature or Player objects)
        controller: a reference to a Player object or None
        magnitude: an integer representing the size of the effect (for effects with {X} in the title)
        required_target_types: a dict of str:int listing each type of target required and how many of 
          of that target are required
        effect_type: a string representing the effect type
        damage_type: if the effect deals damage, deal this type of damage
        narrative_description: says what the effect does, mostly as a prompt
          for image generators
        """

        self.Name = effect_name
        self.Targets = targets or []
        self.Controller = controller
        self.Conditions = conditions or []
        self.Magnitude = int(magnitude)
        self.DamageType = damage_type
        
        #Set RequiredTargets as string then 
        #literal_eval it to get actual data
        self.RequiredTargets = required_target_types or {}
        self.RequiredTargets = ast.literal_eval(self.RequiredTargets)
        self.RequiredTargets = {k:int(v) for k,v in self.RequiredTargets.items()} 
        self.EffectType = effect_type

    def getTargetDescriptions(self):
        """get string describing self.RequiredTargets in words"""
        target_descriptions = []
        for k,v in self.RequiredTargets.items():
            non_numeric_targets = ["all minions","all enemy minions","all players","controller","opponent"]
            if k in non_numeric_targets:
                target_descriptions.append(f"{k}")
            else:
                target_descriptions.append(f"{v} {k}")
        target_text = " and ".join(target_descriptions)
        target_text.replace("controller","you")
        return target_text


    def activate(self):
        """Activate the effect"""
        #Defined by subclasses
        pass

class DealDamage(Effect):
    """Deal {magnitude} damage to required targets"""
    def activate(self):
        """Deal self.Magnitude damage to targets"""
        for t in self.Targets:
            t.takeDamage(amount=self.Magnitude,damage_type=self.DamageType)
    
    def __repr__(self):
        target_text = self.getTargetDescriptions()
        return f"Deals {self.Magnitude} damage to {target_text}"

class Draw(Effect):
    """Targets draw cards"""    
    def activate(self):
        """targets Draw {self.Magnitude} cards"""
        print("self.Targets:",self.Targets)
        for t in self.Targets:
            t.draw(n_cards=self.Magnitude)
    
    def __repr__(self):
         target_text = self.getTargetDescriptions()
         return f"{target_text} draw {self.Magnitude} cards"

class DiscardRandom(Effect):
    """Targets discard random cards"""
    def activate(self):
        """targets discard {self.Magnitude} cards"""
        for t in self.Targets:
            t.discardRandom(n_cards=self.Magnitude)
    
    def __repr__(self):
         target_text = self.getTargetDescriptions()
         return f"{target_text} discards {self.Magnitude} random cards"

class ResurrectRandomCreatures(Effect):
    """Resurrect random creatures"""
    def activate(self):
        """target players resurrect self.Magnitude creatures"""
        for player in self.Targets:
            print(f"Player {player.Name} is about to resurrect {self.Magnitude} random creeatures!") 
            for i in range(self.Magnitude):
                player.resurrectCreature()

    def __repr__(self):
         target_text = self.getTargetDescriptions()
         return f"{target_text} resurrects {self.Magnitude} random creatures"
 

class Heal(Effect):
    """Heal targets of {self.Magnitude} damage"""
    def activate(self):
        """Heal {self.Magnitude} damage to targets"""
        for t in self.Targets:
            t.healDamage(amount=self.Magnitude,damage_type=self.DamageType)
    
    def __repr__(self):
        target_text = self.getTargetDescriptions()
        return f"Heal {target_text} {self.Magnitude}"


class GainManaCrystals(Effect):
    """Controller gains {self.Magnitude} mana crystals"""
    
    def activate(self):
        """Gain {self.Magnitude} mana crystals"""
        if self.Controller:
            self.Controller.gainTotalMana(amount=self.Magnitude)
    
    def __repr__(self):
        return f"Gain {self.Magnitude} mana crystals"     

if __name__ == "__main__":
    #Demo how to set up a game

    #Load set data
    effect_data_filepath = "../data/effect_data/effect_data.txt"
    basic_effects = EffectSet(effect_data_filepath)
    print(basic_effects) 
