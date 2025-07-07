from game.deck import Deck
from game.hand_evaluator import HandEvaluator
from game.player import Player
from game.table import Table

players = []
max_6_pos = ["SB", "BB", "UTG", "HJ", "CO", "BTN"]

for i in range(6):
    players.append(Player(f"Player {i}", 1000))

table = Table()
evaluator = HandEvaluator()

deck = Deck()

# inicio de la mano


