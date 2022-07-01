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
            "draw":Draw
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
 

class Deck(object):

    def __len__(self):
        """Return number of cards in Deck"""
        return(len(self.Cards))

    def __init__(self,cards = None):
        """Initialize a deck of cards
        cards -- a list or deque of Card objects
        The leftmost side of the deque is the 'top' 
        """ 

        self.Cards = deque([])
        if cards:
            self.Cards.extend(cards)

    def draw(self,n_cards=1):
        drawn_cards = []
        for n in range(n_cards):
             if self.Cards:
                curr_card = self.Cards.popleft()
                drawn_cards.append(curr_card)
             else:
                print("Out of Cards!")
        return drawn_cards

    def shuffle(self):
        shuffle(self.Cards)

    def toDeckList(self):
        cards = defaultdict(int)
        for card in self.Cards:
            cards[str(card)] +=1
        return "\n".join(["\t".join([str(k),str(cards[k])]) for k in cards.keys()])


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
        self.RequiredTargets = required_target_types or {}
        self.RequiredTargets = ast.literal_eval(self.RequiredTargets)
        print(self.RequiredTargets)
        self.RequiredTargets = {k:int(v) for k,v in self.RequiredTargets.items()} 
        self.EffectType = effect_type

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
        target_descriptions = []
        for k,v in self.RequiredTargets.items():
            target_descriptions.append(f"{v} {k}")
        target_text = " and ".join(target_descriptions)

        return f"Deal {self.Magnitude} damage to {target_text}"

class Draw(Effect):
    
    def activate(self):
        """targets Draw {self.Magnitude} cards"""
        for t in self.Targets:
            t.draw(n_cards=self.Magnitude)
    
    def __repr__(self):
        return f"Draw {self.Magnitude} cards"

class Heal(Effect):
    """Heal targets of {self.Magnitude} damage"""
    
    def activate(self):
        """Heal {self.Magnitude} damage to targets"""
        for t in self.Targets:
            t.healDamage(amount=self.Magnitude,damage_type=self.DamageType)
    
    def __repr__(self):
        return f"Heal targets {self.Magnitude}"


class GainManaCrystals(Effect):
    """Controller gains {self.Magnitude} mana crystals"""
    
    def activate(self):
        """Gain {self.Magnitude} mana crystals"""
        if self.Controller:
            self.Controller.gainTotalMana(amount=self.Magnitude)
    
    def __repr__(self):
        return f"Gain {self.Magnitude} mana crystals"     
   
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

class Spell(Card):
    def __init__(self,card_name,mana_cost,effects,effect_library,\
      location="",behavior="Temporary Effect",controller = None,types=[],supertype="Spell",portrait_fp=None):
        """A spell 
        card_name -- the name of the card
        mana_cost -- the mana cost of the spell (integer)
        effects -- a list of Effect objects
        """

        self.Name = card_name
        self.Cost = mana_cost
        self.CardType = "Spell"
        self.Behavior = behavior
        self.setUpEffects(effects,effect_library)
        self.setController(controller)
        self.Portrait = portrait_fp
        self.Location = location
        print("Current Location:",location)
        self.CardImageFilepath = self.makeCardImage()
    
    def __repr__(self):
        effects = self.Effects
        if effects:
            effects = ",".join([str(effect) for effect in self.Effects])
        else:
            effects = ""
        return f"{self.Name}({self.Cost}):{effects}"
    
    def makeCardImage(self):
        text = ", ".join([str(effect) for effect in self.Effects])
        cost = self.Cost 
        card_type = self.CardType
        card_name = self.Name
        card_image_dir = get_location_dir(self.Location,base_dir = "../data/images/cards")
        card_filename = filename_from_card_name(self.Name,self.Location)
        
        if self.Effects:
            effects = ", ".join([str(effect) for effect in self.Effects])
        else:
            effects = ""

        card_image_fp = os.path.join(card_image_dir,card_filename)
        if  card_filename not in listdir(card_image_dir):
            card_image_fp = make_game_card(card_name,\
              location = self.Location, card_portrait_filename="generate",\
              card_back_filename="random",attack=None,health=None,\
              cost=cost,card_text = effects,card_type=card_type)         
        return card_image_fp
	
    def setController(self,controller):
        """Set the controller of this Spell and its effects"""
        self.Controller = controller
        for effect in self.Effects:
            effect.Controller = self.Controller
    
    def getTargets(self):
        """Get targets for each effect in the spell, return False if missing targets"""
        required_targets_assigned = True
        for effect in self.Effects:
            for target_type,n_targets in effect.RequiredTargets.items():
                
                effect.Targets = []                
                if target_type == "random enemy minion":
                    #print(f"Targeting {n_targets} random enemy minion(s)")
                    targets = self.Controller.getRandomEnemyMinions(n=n_targets)                
                elif target_type == "all minions":
                    targets = self.Controller.getAllMinions()
                elif target_type == "all enemy minions":
                    #print(f"Targeting {n_targets} random friendly minion(s)")
                    targets = self.Controller.getAllEnemyMinions()                
                elif target_type == "random friendly minion":
                    #print(f"Targeting {n_targets} random friendly minion(s)")
                    targets = self.Controller.getRandomFriendlyMinions(n=n_targets)                
                elif target_type == "random friendly damaged minions":
                    #print(f"Targeting {n_targets} random friendly damaged minion(s)")
                    targets = self.Controller.getRandomFriendlyDamagedMinions(n=n_targets)
                elif target_type == "controller":
                    #print(f"Targeting Controller")
                    targets = [effect.Controller]
                elif target_type == "opponent":
                    #print(f"Targeting Controller")
                    targets = [effect.Controller.Opponent]
                else:
                    raise NotImplementedError(f"Target type {target_type} is not recognized")
                effect.Targets = targets
                if not targets:
                    required_targets_assigned = False
        return required_targets_assigned
       
    def activate(self):
        """Resolve the effects of the Spell"""
        for i,effect in enumerate(self.Effects):
            effect.activate()


class Creature(Card):
    def __init__(self,card_name,effect_library,mana_cost=0,location="",\
        power=0,toughness=0,\
        effects="{}",supertypes="",controller=None,static_abilities="",\
        behavior="Attack Random Enemy",supertype="Creature",types="",portrait_fp=None):
        """Make a new creature card
        """
        self.Name = card_name
        self.Power = int(power)
        self.Toughness = int(toughness)
        self.Cost = int(mana_cost)
        self.CardType = supertype
        self.Behavior = behavior
        self.Location = location
        self.CurrentHealth = self.Toughness
        self.Dead = False
        self.Controller = controller
        self.StaticAbilities = static_abilities.split(",")
        self.SuperTypes = supertypes.split(",") 
        self.Types = types.split(",")
        self.setUpEffects(effects,effect_library)
        self.Portrait = portrait_fp
        print("Current Location:",location)
        self.CardImageFilepath = self.makeCardImage()

    def __repr__(self):
        if self.checkIfDead():
            return f"{self.Name} (Dead)"
        return f"{self.Name}({self.Cost}):{self.Power}/{self.CurrentHealth}"

    def makeCardImage(self):
        text = "Action — "+self.Behavior + "\n" + ", ".join([str(effect) for effect in self.Effects]) +"\n " + ", ".join(self.StaticAbilities)
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
              card_back_filename="random",\
              attack= self.Power,health= self.Toughness,\
              cost=cost,card_text = text,card_type=card_type)
        else:
            card_image_fp = os.path.join(card_image_dir,card_filename)
        return card_image_fp
 
    def attack(self,target):
        """Resolve an attack"""

        print(f"{self.Name} attacks {target.Name} for {self.Power} damage")        
        damage_dealt = self.dealDamage(target,self.Power)
        print(f"After all abilities are resolved, {target.Name} takes {damage_dealt} damage")
        
        #Ranged creatures only suffer damage when defending,
        #and only deal damage when attacking
        if "Creature" in target.SuperTypes and\
            "Ranged" not in target.StaticAbilties and\
            "Ranged" not in self.StaticAbilities:
            print(f"{creature.Name} takes {target.Power} damage")
            target.dealDamage(target=self,amount=target.Power)
        elif "Ranged" in self.StaticAbilities:
            print(f"{target.Name} doesn't get a chance to attack back because {self.Name} is Ranged")
 
        if "Parasitic" in self.StaticAbilities:
            print(f"{self.Name} parasitises {target.Name} for {damage_dealt} Health")            
            self.healDamage(damage_dealt)
 
    def canAttack(self,target):
        """Return True if it is possible, in general, to attack target"""

        if "Player" in target.SuperTypes:
            return True

        if "Creature" not in target.SuperTypes:
            return False
        
        if "Flying" in target.StaticAbilities\
          and "Flying" not in self.StaticAbilities\
            and "Ranged" not in self.StaticAbilities:
            return False
        
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
                    break #don't play later copies
    
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
 
    def checkIfDead(self):    
        
        if self.Dead or self.CurrentHealth == 0:
            return True
        else: 
            return False


class Player(object):
    def __init__(self,deck,health=20,name="Unknown Player",total_mana=0):
        self.Name = name

        self.Health = health
        self.MaxHealth = self.Health

        self.TotalMana = total_mana
        self.CurrentMana = self.TotalMana
        self.Opponent = None
        self.Deck = deck
        self.Deck.shuffle()
        self.Hand = self.Deck.draw(3)
        self.SuperTypes = ["Player"]
        self.Board = []
        self.MaxBoardSize = 7
    
    def __repr__(self):
        return f"{self.Name} ({self.Health} health)"

    def handAsStr(self,delimiter=","):
        """Return cards in hand as string""" 
        return delimiter.join(map(str,self.Hand))

    def refreshMana(self):
        """Set current mana to total mana"""
        self.CurrentMana = self.TotalMana

    def takeDamage(self,amount=1,damage_type="physical",verbose=True):
        """Deal damage to the player"""
        self.Health -= amount
        self.Health = max(0,self.Health)
        print(f"{self.Name} falls to {self.Health} health")
        return amount

    def healDamage(self,amount=1):
        """Heal a certain amount of damage"""
        self.CurrentHealth += amount
        self.CurrentHealth = min(self.CurrentHealth,self.MaxHealth) 

    def getRandomEnemyMinions(self,n=1):
        """Return a list of n random enemy minions (allowing double-targeting) or None"""
        
        targets = []
        if not self.Opponent or not self.Opponent.Board:
            return targets  
         
        enemy_board = self.Opponent.Board
        for i in range(n):
            random_enemy_minion = choice(enemy_board)
            targets.append(random_enemy_minion)
        return targets       
    
    def getAllMinions(self):
        """Return a list of all minions"""
        targets = []
        targets.extend(self.getAllEnemyMinions())
        targets.extend(self.getAllFriendlyMinions())     
        return targets
 
    def getAllEnemyMinions(self):
        """Return a list of all enemy minions or None"""
        
        targets = []
        if not self.Opponent or not self.Opponent.Board:
            return targets  
         
        targets = self.Opponent.Board
        return targets       

    def getAllFriendlyMinions(self):
        """Returns a list of all friendly minions"""
        
        targets = []
        if not self.Board:
            return targets

        targets = self.Board
        return targets

    def getRandomFriendlyMinions(self,n=1,positive_filter_method_name=None):
        """Return a list of n random friendly minions (allowing double-targeting) or None
        n: number of (not necessarily unique) targets to pick
        filter_method_name: run this method of each creature; only choose among those that
         return True
        """
        targets = []
        board = self.Board
        if not board:
            return targets  
        
         
        for i in range(n):
            random_friendly_minion = choice(board)
            targets.append(random_friendly_minion)

        return targets       
    
    def getRandomFriendlyDamagedMinions(self,n=1):
        """Return a list of n random friendly minions or None"""
        targets = []
        board = self.Board
        if not board:
            return targets
        
        damaged_creatures = self.filterBoard(positive_filter_method_name="isDamaged")
        if not damaged_creatures:
            return targets
        
        for i in range(n):
            targets.append(choice(damaged_creatures))
   
     
    def filterBoard(self,positive_filter_method_name=None,positive_filter_kwargs = {},\
      negative_filter_method_name=None,negative_filter_kwargs={}):
        """Return all minions on board that pass positive filter but not negative filter"""
        all_creatures = [creature for creature in self.Board]
        filtered_creatures = []
        for t in all_creatures:
            
            if positive_filter_method_name:
                passed_pos_filter = getattr(t,positive_filter_method_name)(**positive_filter_kwargs)
                if not passed_pos_filter:
                    continue 
 
            if negative_filter_method_name:
                passed_neg_filter = not getattr(t,negative_method_filter_name)(**negative_filter_kwargs)
                if not passed_neg_filter:
                    continue
        
            filtered_creatures.append(t)
        
        return filtered_creatures     
         

    def gainTotalMana(self,amount):
        """Gain total mana"""
        self.TotalMana += amount
        print(f"{self.Name} goes up to {self.TotalMana} mana")    
    
    def gainCurrentMana(self,amount):
        """Gain current mana"""
        self.CurrentMana += amount

    def draw(self,n_cards=1):
        """Draw n cards"""

        print(f"{self.Name} drew the following {n_cards} cards:")
        drawn_cards = self.Deck.draw(n_cards)
        print(",".join(map(str,drawn_cards)))
        self.Hand.extend(drawn_cards)        

    def playCard(self,card,verbose=True):
        """Play a card from hand"""

        if card not in self.Hand:
            print("Can't play card - not in hand")
            return None
        
        if card.Cost > self.CurrentMana:
            print("Can't play card - not enough mana")
            return None

        else:
            for i,hand_card in enumerate(self.Hand):
                if hand_card == card:
                    #print("Removing 1 copy of card from hand")
                    self.Hand.pop(i)
                    break #don't play later copies
            
            if card.CardType == "Creature":
                #print("Playing card as creature")
                if len(self.Board) < self.MaxBoardSize: 
                    self.Board.append(card)
                    print(f"{self.Name} plays {card.Name}")
                    self.CurrentMana -= card.Cost
                    card.Controller = self
            elif card.CardType == "Spell":
                self.CurrentMana -= card.Cost
                card.setController(self)
                print(f"{self.Name} plays {card.Name}")
                card.getTargets()
                card.activate()  
            else:
                raise NotImplementedError(f"Card type {card.CardType} not yet supported")
    
    def highestCostPlayableCard(self):
        """Return the highest cost playable card in hand"""
        highest_cost_card = None
        max_cost = None
        for card in self.Hand:
            if not max_cost or card.Cost > max_cost:
                if card.Cost <= self.CurrentMana:
                    if card.CardType == "Spell":
                        card.setController(self)
                        if not card.getTargets():
                            continue
                        else:
                            #Need to reset targets
                            card.Targets = []
                    highest_cost_card = card
                    max_cost = card.Cost

        return highest_cost_card

class Game(object):
    def __init__(self,player_1,player_2):
        self.Player1 = player_1
        self.Player2 = player_2

        self.Player1.Opponent = self.Player2
        self.Player2.Opponent = self.Player1

        #Shuffle cards
        self.Player1.Deck.shuffle()
        self.Player2.Deck.shuffle()

        self.PlayOrder = [self.Player1,self.Player2]
        self.Phases = ["Gain Mana","Refresh Mana","Draw","Start of Turn",\
          "Action","Play","End of Turn"]
        self.Winner = None

    def takeTurn(self,player):
        print("="*20)
        print(f"-- {player.Name}'s turn! {player.Health} / {player.MaxHealth} --")
        print("="*20)
        for phase in self.Phases:
            self.doPhase(player,phase)    

    def runGame(self,wait_for_input=True):
        player1 = self.Player1
        player2 = self.Player2
        turn = 0
        while player1.Health > 0 and player2.Health >0:
            turn += 1
            print(f"--- Start of Turn {turn} ---")
            for player in self.PlayOrder:
                self.takeTurn(player)
                input("Ready to move on?")
        
        if player1.Health <= 0 and player2.Health <=0:
            print("Both players die. Tie game!")
        elif player1.Health <=0:
            print(f"{player2.Name} is victorious!")
            self.Winner = player2
        elif player2.Health <=0:
            print(f"{player1.Name} is victorious!")
            self.Winner = player1
        return self.Winner

    def doPhase(self,player,phase):
        print(f"\n - Phase: {player.Name} {phase} -") 
        if phase == "Gain Mana":
            player.gainTotalMana(amount=1)
        
        if phase == "Refresh Mana":
            player.refreshMana() 
        
        if phase == "Draw":
            player.draw()
            hand = player.handAsStr(delimiter="\n")
            hand_size = len(player.Hand)
            print(f"{player.Name} has the following {hand_size} cards in hand:\n{hand}")

        if phase == "Play":
            self.playPhase(player)

        if phase == "Action":
            self.actionPhase(player)
           
    def actionPhase(self,player):
        """Take actions"""
        print(f"{player.Name}'s Board:\n{player.Board}")
        print(f"{player.Opponent.Name}'s Board:\n{player.Opponent.Board}")
        for creature in player.Board:
            if creature is None:
                continue
            
            if creature.Behavior == "Attack Random Enemy":
                

                attacker_ranged = False
                attacker_flying = True

                if "Flying" in creature.StaticAbilities:
                    attacker_flying = True

                #first check to see if any creatures have Defender
                targets_with_defender =\
                  player.Opponent.filterBoard(positive_filter_method_name="hasAbility",\
                  positive_filter_kwargs={"ability":"Defend"})

                
                if targets_with_defender and not attacker_ranged:
                    targets = targets_with_defender
                    targets = [t for t in targets if creature.canAttack(t)]
                else:
                     targets = [player.Opponent]
                     targets.extend([c for c in player.Opponent.Board if creature.canAttack(c)])

                if targets:
                    target = choice(targets)
                    print(f"{creature.Name} attacks {target.Name} for {creature.Power} damage")
                    creature.attack(target)

            elif creature.Behavior == "Attack Opponent":
                #first check to see if any creatures have Defender
                targets_with_defender =\
                  player.Opponent.filterBoard(positive_filter_method_name="hasAbility",\
                  positive_filter_kwargs={"ability":"Defend"})
                if targets_with_defender:
                    target = choice(targets_with_defender)
                else:
                    target = player.Opponent
                print(f"{creature.Name} attacks {target.Name} for {creature.Power} damage")
                target.takeDamage(creature.Power) 
            elif creature.Behavior == "Defend":
                pass

    def playPhase(self,player):
        """Do a play phase
        For now players will play the highest cost card possible
        """
        highest_cost_card = player.highestCostPlayableCard()
        print("Highest cost card:",highest_cost_card)
        while highest_cost_card:
            print("Player decides to play card:",highest_cost_card)     
            player.playCard(highest_cost_card)
            highest_cost_card = player.highestCostPlayableCard()
            if highest_cost_card is None:
                break
        
        print(f"{player.Name}'s Board:\n{player.Board}")
        print(f"{player.Opponent.Name}'s Board:\n{player.Opponent.Board}")

def load_deck(deck_path,card_library):
    """Load a deck
    deck_path -- path to a .tsv file for the deck

    deck .tsv files should have card_name\tcopies
    all card names *must* be in the card_data file
    """
    print(f"Loading deck from path {deck_path}")
    decklist = pd.read_csv(deck_path,"\t")
    card_names=list(decklist["card_name"])
    decklist.set_index("card_name",inplace=True,drop=False)
    decklist.dropna(axis=0,how="all", inplace=True)
    decklist.dropna(axis=1,how="all", inplace=True)
    print("About to build deck from decklist:",decklist)
    deck = []
    print("Unique cards in decklist:",card_names)
    for card_name in card_names:
        copies = decklist.loc[card_name,"copies"]
        print(f"Making {card_name} x{copies}")
        this_card = card_library.makeCards([card_name],copies)
        print("Current card:",this_card)
        deck.extend(this_card)
        print("Deck:",deck)
    print("Loaded a deck with these cards:",deck)
    return deck

if __name__ == "__main__":
    #Demo how to set up a game

    #Load set data
    card_data_filepath = "../data/card_data/basic_card_set.txt"
    effect_data_filepath = "../data/effect_data/effect_data.txt"
    basic_effects = EffectSet(effect_data_filepath)
    basic_cards = CardSet(card_data_filepath,effect_library=basic_effects)

    #Load decks
    player_1_name = "Player"
    player_1_deck_path = "../data/decks/latest_player_draft.tsv"
    player_1_deck_cards = load_deck(player_1_deck_path,card_library=basic_cards)
    player_1_deck = Deck(player_1_deck_cards)
    print(f"{player_1_name} decklist:", player_1_deck.toDeckList())
    player_1 = Player(name=player_1_name,deck=player_1_deck)

    player_2_name = "King Kyber"
    player_2_deck_path = "../data/decks/King_Kyber_starter_deck.txt"
    #player_2_name = "Bloodtusk"
    #player_2_deck_path = "../data/decks/Bloodtusk_starter_deck.txt"
    player_2_deck_cards = load_deck(player_2_deck_path,card_library=basic_cards)
    player_2_deck = Deck(player_2_deck_cards)
    print(f"{player_2_name} decklist:", player_2_deck.toDeckList()) 
    player_2 = Player(name = player_2_name,deck=player_2_deck)
   
    print("ABOUT TO RUN GAME!!!!!") 
    #Run game
    game = Game(player_1,player_2)
    game.runGame() 
