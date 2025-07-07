from typing import List

from game.deck import Deck
from game.player import Player
from game.hand_evaluator import HandEvaluator

stages = {"PREFLOP": 0, "FLOP": 1, "TURN": 2, "RIVER": 3}

class Table:
    def __init__(self, players: List[Player] = None):
        self.type = len(players)
        self.deck = Deck()
        self.comon = []
        self.pot = 0
        self.stage = 0
        self.dealer_index = 0
        self.players = players if players else []

    def new_hand(self):
        self.deck.reset_cards()
        self.comon = []
        self.pot = 0
        self.stage = 0
        for p in self.players:
            p.reset()
            p.in_game = True
            p.last_action = None

    def next_stage(self):
        self.stage += 1

    def deal_comon(self, n: int = 1):
        for _ in range(n):
            card = self.deck.deal()[0]
            self.comon.append(card)

    def resolve_winner(self):
        evaluator = HandEvaluator()
        players_in_showdown = [p for p in self.players if p.in_game and p.hand]

        if not players_in_showdown:
            print("No hay jugadores activos en showdown.")
            return []

        # Calcular side pots
        all_bets = sorted(set(p.current_bet for p in self.players if p.current_bet > 0))
        side_pots = []  # (monto, jugadores)

        previous = 0
        remaining_players = self.players[:]

        for bet in all_bets:
            contributors = [p for p in remaining_players if p.current_bet >= bet]
            pot_size = (bet - previous) * len(contributors)
            side_pots.append((pot_size, contributors))
            previous = bet
            # Elimina jugadores con stack igual a ese bet (all-in exacto)
            remaining_players = [p for p in remaining_players if p.current_bet > bet]

        winners_summary = []
        remaining_pot = self.pot

        print("\n--- Showdown ---")
        for p in players_in_showdown:
            full_hand = p.hand + self.comon
            best = evaluator.evaluate_best_hand(full_hand)
            print(f"{p.name} => {best}")

        # Resolver cada side pot
        for i, (pot_amount, contributors) in enumerate(side_pots):
            contenders = [p for p in players_in_showdown if p in contributors]
            if not contenders:
                continue

            best_score = max(evaluator.evaluate_best_hand(p.hand + self.comon) for p in contenders)
            winners = [p for p in contenders if evaluator.evaluate_best_hand(p.hand + self.comon) == best_score]

            split = pot_amount // len(winners)
            remainder = pot_amount % len(winners)
            remaining_pot -= pot_amount

            for w in winners:
                w.stack += split
            if remainder > 0:
                winners[0].stack += remainder

            winners_summary.append((winners, pot_amount))

        print("\n--- Resultados ---")
        for winners, pot in winners_summary:
            names = ", ".join(w.name for w in winners)
            print(f"{names} ganan {pot} fichas")

        return winners_summary

    def register_event(self, player, event):
        pass
