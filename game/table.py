from typing import List

from game.side_pot_manager import SidePotManager
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
        self.players = players
        self.btn_index = 0
        self.deck.reset_cards()
        self.side_pot_manager = SidePotManager()
        self.evaluator = HandEvaluator()

        for p in self.players:
            p.reset()

    def new_hand(self):
        self.deck.reset_cards()
        self.comon = []
        self.pot = 0
        self.stage = 0
        for p in self.players:
            p.reset()
        self.btn_index = (self.btn_index + 1) % 6
        self.side_pot_manager.reset()

    def next_stage(self):
        self.stage = (self.stage + 1) % 4

    def assign_positions(self):
        position_names = ["BTN", "SB", "BB", "UTG", "HJ", "CO"]
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
            highest_bet = bb_player.current_bet

        # Orden en el que los jugadores actuarán
        action_order = [self.players[(starting_index + i) % self.type] for i in range(self.type)]

        while True:
            all_acted = True

            for player in action_order:
                if not player.in_game or player.all_in or last_to_raise == player:
                    continue

                to_call = highest_bet - player.current_bet

                if player.ai_controller is not None:
                    hand = player.hand + self.comon
                    strength = self.evaluator.get_strength_ratio(hand)
                    player.ai_controller.update_strength_estimate(strength)
                    decision = player.ai_controller.decide(player, self.comon, self.stage)
                else:
                    decision = player.decide()

                action = decision.get("action")

                if action == "fold":
                    player.in_game = False
                    print(f"{player} folds")

                elif action == "call":
                    actual_bet = player.bet(to_call)
                    stage_pot += actual_bet
                    print(f"{player} calls with {actual_bet}")

                elif action == "check":
                    if to_call > 0:
                        # No puede hacer check si hay algo por pagar
                        print(f"{player.name} intentó hacer check pero hay que pagar {to_call}. Por tanto fold")
                        player.in_game = False  # o podrías pedirle otra acción, según tu lógica
                    else:
                        print(f"{player.name} hace check.")

                elif action == "all_in":
                    actual_bet = player.bet(player.stack)
                    stage_pot += actual_bet
                    player.all_in = True
                    if player.current_bet > highest_bet:
                        highest_bet = player.current_bet
                        last_to_raise = player
                        all_acted = False
                    print(f"{player} allin with {actual_bet}")

                elif action in ["raise", "bet"]:
                    target_amount = decision.get("amount", 0)
                    raise_amount = max(0, target_amount - player.current_bet)
                    actual_bet = player.bet(raise_amount)
                    stage_pot += actual_bet

                    if player.current_bet > highest_bet:
                        highest_bet = player.current_bet
                        last_to_raise = player
                        all_acted = False

                    print(f"{player} bets with {actual_bet}")

            if all_acted or all(not p.in_game or p.all_in or p.current_bet == highest_bet for p in self.players):
                break
        return stage_pot

    def deal_comon(self, n: int = 1):
        for _ in range(n):
            card = self.deck.deal()[0]
            self.comon.append(card)

    def resolve_winner(self):
        evaluator = self.evaluator
        players_in_showdown = [p for p in self.players if p.in_game and p.hand]

        if not players_in_showdown:
            print("No hay jugadores activos en showdown.")
            return []

        self.side_pot_manager.collect_bets(self.players)
        self.side_pot_manager.create_pots()

        print("\n--- Showdown ---")
        for p in players_in_showdown:
            full_hand = p.hand + self.comon
            best = evaluator.evaluate_best_hand(full_hand)
            print(f"{p.name} => {best}")

        results = self.side_pot_manager.resolve_pots(evaluator, self.comon)

        print("\n--- Resultados ---")
        for i, (winners, pot) in enumerate(results):
            names = ", ".join(w.name for w in winners)
            if i == 0:
                print(f"{names} gana el **main pot** de {pot} fichas")
            else:
                print(f"{names} gana el **side pot {i}** de {pot} fichas")

        return results

    def register_event(self, player, event):
        pass
