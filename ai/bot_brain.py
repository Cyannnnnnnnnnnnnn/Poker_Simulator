import random

class SimplePokerAI:
    def __init__(self):
        self.strength_estimate = 0.0

    def update_strength_estimate(self, strength: float):
        self.strength_estimate = strength

    def decide(self, player, community_cards, stage):
        """
        Retorna una acción en forma de diccionario: {"action": ..., "amount": ...}
        Basado en la fuerza estimada de la mano y un poco de aleatoriedad.
        """
        # Si el jugador ya está all-in, no puede hacer nada
        if player.stack == 0:
            return {"action": "check"}

        # Estrategia básica
        if self.strength_estimate > 0.85:
            # Mano muy fuerte: sube fuerte
            return {"action": "raise", "amount": player.current_bet + min(player.stack, 150)}
        elif self.strength_estimate > 0.65:
            # Mano decente: hace call o raise chico
            if random.random() < 0.5:
                return {"action": "call"}
            else:
                return {"action": "raise", "amount": player.current_bet + min(player.stack, 50)}
        elif self.strength_estimate > 0.4:
            # Mano mediocre: hace call o check
            if player.current_bet == 0:
                return {"action": "check"}
            else:
                return {"action": "call"}
        else:
            # Mano mala: fold o check
            if player.current_bet == 0:
                return {"action": "check"}
            else:
                return {"action": "fold"}
