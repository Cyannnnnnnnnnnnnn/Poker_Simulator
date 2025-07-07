import random
from typing import List

suits = ["s", "h", "c", "d"]
values = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]

class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def __repr__(self):
        return f"{self.value}{self.suit}"

class Deck:
    def __init__(self):
        self.cards : List[Card] = [Card(value, suit) for suit in suits for value in values]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, n: int = 1) -> List[Card]:
        cards : List[Card] = []
        for i in range(n):
            cards.append(self.cards.pop())
        return cards

    def burn(self):
        self.cards.pop()

    def reset_cards(self):
        self.cards: List[Card] = [Card(value, suit) for suit in suits for value in values]
        self.shuffle()

    def __repr__(self):
        return " ".join(str(card) for card in self.cards)

