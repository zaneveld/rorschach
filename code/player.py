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
        self.CardType = "Player"
        self.Board = []
        self.MaxBoardSize = 7
        self.Graveyard = []
 
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
   
     
    def filter(self,iterable,positive_filter_method_name=None,positive_filter_kwargs = {},\
      negative_filter_method_name=None,negative_filter_kwargs={}):
        """Return all minions on board that pass positive filter but not negative filter"""
        all_creatures = [creature for creature in iterable]
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
         
    def filterBoard(self,*args,**kwargs):
        """Convenience method to call filter on the player's board"""
        iterable = self.Board
        return self.filter(iterable,*args,**kwargs)

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

    def removeCardFromHand(self,card):
        """Discard a specific card"""
        for i,hand_card in enumerate(self.Hand):
                if hand_card == card:
                    removed_card = self.Hand.pop(i)
                    return removed_card 

    def discardRandom(self,n_cards):
        """Discard n_cards Cards from Hand at random"""
        discarded_cards = []
        for i in range(n_cards):
            if not self.Hand:
                print("Hand is empty, can't discard more cards")
                return discarded_cards

            random_card_in_hand = choice(self.Hand)
            current_discard = self.removeCardFromHand(random_card_in_hand)
            discarded_cards.append(current_discard)

    def playCard(self,card,verbose=True):
        """Play a card from hand"""

        if card not in self.Hand:
            print("Can't play card - not in hand")
            return None
        
        if card.Cost > self.CurrentMana:
            print("Can't play card - not enough mana")
            return None
        else:
            card = self.removeCardFromHand(card)
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
    
    def resurrectCreature(self,max_mana_cost = None, required_type = None, required_static_ability = None, required_supertype = "Creature"):
        """Resurrect a creature with conditions"""
        
        if not self.Graveyard:
            return False
        
        possible_targets = [card for card in self.Graveyard if required_supertype in card.CardType]
        
        if not possible_targets:
            return False

        if max_mana_cost:
            possible_targets = [t for t in possible_targets if t.Cost <= max_mana_cost]
        
        if not possible_targets:
            return False

        if required_type:
            possible_targets = [t for t in possible_targets if required_type in t.Types]

        if not possible_targets:
            return False
        
        target = choice(possible_targets)
        self.returnCreatureToPlay(target) 
        
        return 

    def returnCreatureToPlay(self,creature):
        """Return a creature to play"""
        if len(self.Board) > self.MaxBoardSize:
            print(f"Can't resurrect {creature.Name}, board is full ({len(self.Board)/self.MaxBoardSize})")
            return False
        if not self.Graveyard:
            print("Can't resurrect anything - nothing in Graveyard")
            return False
        for i,c in enumerate(self.Graveyard):
            if c is creature:
                c.Alive = True   
                creature = self.Graveyard.pop(i)
                self.Board.append(creature)
                break

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

