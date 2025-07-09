# game/side_pot_manager.py

class SidePotManager:
    def __init__(self):
        self.pots = []  # Lista de tuplas: (monto, lista de jugadores contribuyentes)

    def reset(self):
        self.pots.clear()

    def collect_bets(self, players):
        self.bets = sorted(
            [(p, p.current_bet) for p in players if p.current_bet > 0],
            key=lambda x: x[1]
        )
        self.players = players

    def create_pots(self):
        """Crea los side pots basados en las apuestas actuales"""
        remaining = self.bets.copy()
        last_bet = 0

        while remaining:
            # El siguiente nivel de apuesta más bajo
            min_bet = remaining[0][1]
            diff = min_bet - last_bet

            # Contribuyentes a este nivel
            contributors = [p for p, b in remaining if b >= min_bet]

            # Tamaño del side pot
            pot_size = diff * len(contributors)
            self.pots.append((pot_size, contributors.copy()))
            last_bet = min_bet

            # Reducir las apuestas en este nivel
            remaining = [(p, b) for p, b in remaining if b > min_bet]

    def resolve_pots(self, evaluator, community_cards):
        resultados = []

        for pot_amount, contributors in self.pots:
            active_contributors = [p for p in contributors if p.in_game]

            if not active_contributors:
                continue

            # Evaluar manos
            best_score = max(
                evaluator.evaluate_best_hand(p.hand + community_cards)
                for p in active_contributors
            )

            winners = [
                p for p in active_contributors
                if evaluator.evaluate_best_hand(p.hand + community_cards) == best_score
            ]

            # Repartir el pozo
            share = pot_amount // len(winners)
            remainder = pot_amount % len(winners)

            for winner in winners:
                winner.stack += share

            if remainder > 0:
                winners[0].stack += remainder

            resultados.append((winners, pot_amount))

        return resultados
