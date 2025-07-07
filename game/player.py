from typing import List

from game.deck import Card

max_6_pos = ["SB", "BB", "UTG", "HJ", "CO", "BTN"]
max_9_pos = ["SB", "BB", "UTG", "EP2", "MP", "MP2", "HJ", "CO", "BTN"]

class Player:
    def __init__(self, name, stack: int, is_human: bool = False):
        self.name = name
        self.hand = None
        self.stack = stack
        self.in_game = True
        self.is_human = is_human
        self.pos = 0
        self.last_action = None
        self.current_bet = 0

    def bet(self, amount: int):
        real_bet = min(self.stack, amount)
        self.stack -= real_bet
        self.current_bet += real_bet
        if self.stack == 0:
            print(f"{self.name} está all-in con {self.current_bet}")
        return real_bet

    def set_hand(self, new_hand):
        self.hand = new_hand


    def fold(self):
        self.in_game = False

    def reset(self):
        self.hand = []
        self.current_bet = 0
        self.in_game = True

    def decide(self):
        pass

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()
