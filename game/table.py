from typing import List

from game.deck import Deck
from game.player import Player
from game.hand_evaluator import HandEvaluator

stages = {0: 'PREFLOP', 1: 'FLOP', 2: 'TURN', 3: 'RIVER'}

class Table:
    def __init__(self, players: List[Player], deck):
        self.type = len(players)
        self.deck = deck
        self.comon = []
        self.pot = 0
        self.stage = 0
        self.dealer_index = 0
        self.players = players
        self.btn_index = 0

    def new_hand(self):
        self.deck.reset_cards()
        self.comon = []
        self.pot = 0
        self.stage = 0
        for p in self.players:
            p.reset()
            p.in_game = True
            p.last_action = None
        self.dealer_index = (self.dealer_index + 1) % 6

    def next_stage(self):
        self.stage = (self.stage + 1) % 4

    def assign_positions(self):
        position_names = ["BTN", "SB", "BB", "UTG", "MP", "CO"]
        for i in range(self.type):
            self.players[(self.btn_index + i) % self.type].pos = position_names[i]

    def _get_starting_index(self):
        if self.stage == 0:
            return (self.btn_index + 3) % len(self.players)
        else:
            return (self.btn_index + 1) % len(self.players)

    def start_betting_round(self):
        starting_index = self._get_starting_index()
        stage_pot = 0
        highest_bet = 0
        last_to_raise = None

        if self.stage == 0:
            sb_index = (self.btn_index + 1) % self.type
            bb_index = (self.btn_index + 2) % self.type

            sb_player = self.players[sb_index]
            bb_player = self.players[bb_index]

            sb_amount = sb_player.bet(25)
            bb_amount = bb_player.bet(50)

            stage_pot += sb_amount + bb_amount
            highest_bet = bb_player.current_bet  # BB define la apuesta mínima inicial

        # Orden en el que los jugadores actuarán
        action_order = [self.players[(starting_index + i) % self.type] for i in range(self.type)]

        while True:
            all_acted = True

            for player in action_order:
                if not player.in_game or player.all_in:
                    continue

                to_call = highest_bet - player.current_bet
                decision = player.decide()
                action = decision.get("action")

                if action == "fold":
                    player.in_game = False

                elif action == "call":
                    actual_bet = player.bet(to_call)
                    stage_pot += actual_bet

                elif action == "check":
                    if to_call > 0:
                        # No puede hacer check si hay algo por pagar
                        print(f"{player.name} intentó hacer check pero hay que pagar {to_call}. Por tanto fold")
                        player.in_game = False  # o podrías pedirle otra acción, según tu lógica
                    else:
                        print(f"{player.name} hace check.")


                elif action == "allin":
                    actual_bet = player.bet(player.stack)
                    stage_pot += actual_bet
                    player.all_in = True
                    if player.current_bet > highest_bet:
                        highest_bet = player.current_bet
                        last_to_raise = player
                        all_acted = False

                elif action in ["raise", "bet"]:
                    amount = decision.get("amount", 0)
                    desired_total = amount
                    raise_amount = desired_total - player.current_bet

                    actual_bet = player.bet(desired_total)
                    stage_pot += actual_bet

                    if player.current_bet > highest_bet:
                        highest_bet = player.current_bet
                        last_to_raise = player
                        all_acted = False

            if all_acted or all(not p.in_game or p.all_in or p.current_bet == highest_bet for p in self.players):
                break
        return stage_pot

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
