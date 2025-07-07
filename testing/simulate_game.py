from game.deck import Deck
from game.hand_evaluator import HandEvaluator
from game.player import Player
from game.table import Table

num_players = 6

players = []

for i in range(6):
    players.append(Player(f"Player {i}", 1000))

deck = Deck()
table = Table(players, deck)
evaluator = HandEvaluator()

#Asign positions
table.assign_positions()
table.new_hand()

for player in players:
    player.set_hand(deck.deal(2))

#PREFLOP

table.pot += table.start_betting_round()
print(table.pot)
for player in players:
    print(f"{player.name} stack: {player.stack}, current_bet: {player.current_bet}")




