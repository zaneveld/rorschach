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
from card import Card,Spell,Creature,CardSet
from deck import Deck,load_deck





class GameInterface(object):
    def __init__(self):
        pass

    def report(self,free_text,specific_event,specific_event_props={}):
        print(free_text)




class Game(object):
    def __init__(self,player_1,player_2,game_interface=None):
        self.Player1 = player_1
        self.Player2 = player_2
        self.Player1.Game = self
        self.Player2.Game = self        
        self.Interface = game_interface
        if self.Interface == None:
            self.Interface = GameInterface()
       
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
        """Run the game

        wait_for_input -- wait to show each turn until player
          responds to input prompt
        """
        player1 = self.Player1
        player2 = self.Player2
        turn = 0
        while player1.Health > 0 and player2.Health >0:
            turn += 1
            print(f"--- Start of Turn {turn} ---")
        
            for player in self.PlayOrder:
                self.takeTurn(player)
                input("Ready to move on?")
       
        self.Winner = self.checkForLoss(player1,player2)        
        return self.Winner
        
        
    def checkForLoss(self,player1,player2):
        """Check if a player lost, or return None if game is ongoing"""
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
                attacker_flying = False

                if "Flying" in creature.StaticAbilities:
                    attacker_flying = True
                if "Ranged" in creature.StaticAbilities:
                    attacker_ranged = True

                #first check to see if any creatures have Defender
                targets_with_defender =\
                  player.Opponent.filter(player.Opponent.Board,positive_filter_method_name="hasAbility",\
                  positive_filter_kwargs={"ability":"Defend"})
                
                if targets_with_defender:
                    print(f"The following enemy creatures have Defend: {[t.Name for t in targets_with_defender]}")
                targets = []
                if targets_with_defender and not attacker_ranged:
                    print("Some enemies have defender and attacker is not ranged ... it must target a creature with defender")
                    targets = targets_with_defender
                    targets = [t for t in targets if creature.canAttack(t)]
                    if not targets:
                        print("Couldn't attack any enemies with Defender")
                #If we didn't resolve Defend abilities
                #or no Defenders can be attacked, pick a random target we can attack
                if not targets:
                      
                     targets = [player.Opponent]
                     for possible_target in player.Opponent.Board:
                        can_attack = creature.canAttack(possible_target)
                        print(f"{creature.Name} can attack {possible_target.Name} --> {can_attack}")
                        if can_attack:
                            targets.append(possible_target)
                
                if targets:
                    print(f"Choosing randomly from the following targets: {[t.Name for t in targets]}")
                    target = choice(targets)
                    creature.attack(target)

            elif creature.Behavior == "Attack Opponent":
                #first check to see if any creatures have Defender
                targets_with_defender =\
                  player.Opponent.filter(player.Board,positive_filter_method_name="hasAbility",\
                  positive_filter_kwargs={"ability":"Defend"})
                if targets_with_defender:
                    target = choice(targets_with_defender)
                else:
                    target = player.Opponent
                print(f"{creature.Name} attacks {target.Name} for {creature.Power} damage")
                target.takeDamage(creature.Power) 
            elif creature.Behavior == "Defend":
                pass
            elif creature.Behavior == "Activate":
                print(f"{creature.Name} is activating it's ability")
                for e in creature.Effects:
                    e.Controller = creature.Controller
                
                found_target = creature.getTargets()
                if found_target:
                    creature.activate() 

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
