from game.deck import Deck
from game.player import Player
from game.table import Table
from ai.bot_brain import SimplePokerAI as PokerAI  # Asegúrate de haber definido esta clase

# Crear jugadores con IA
players = [
    Player("Bot 0", 1000, is_human=False, ai_controller=PokerAI()),
    Player("Bot 1", 1000, is_human=False, ai_controller=PokerAI()),
    Player("Bot 2", 1000, is_human=False, ai_controller=PokerAI()),
    Player("Bot 3", 1000, is_human=False, ai_controller=PokerAI()),
    Player("Bot 4", 1000, is_human=False, ai_controller=PokerAI()),
    Player("Bot 5", 1000, is_human=False, ai_controller=PokerAI())
]

deck = Deck()
table = Table(players, deck)

# Iniciar mano nueva
table.new_hand()
table.assign_positions()

# Repartir manos privadas
for p in players:
    p.set_hand(deck.deal(2))

# Mostrar manos iniciales
print("\n--- Manos preflop ---")
for p in players:
    print(f"{p.name}: {p.hand}")

# Preflop
print("\n--- Preflop ---")
pot = table.start_betting_round()
table.pot += pot
print(f"Pot: {table.pot}")

# Flop
table.next_stage()
table.deal_comon(3)
print("\n--- Flop ---")
print("Comunitarias:", table.comon)
pot = table.start_betting_round()
table.pot += pot
print(f"Pot: {table.pot}")

# Turn
table.next_stage()
table.deal_comon(1)
print("\n--- Turn ---")
print("Comunitarias:", table.comon)
pot = table.start_betting_round()
table.pot += pot
print(f"Pot: {table.pot}")

# River
table.next_stage()
table.deal_comon(1)
print("\n--- River ---")
print("Comunitarias:", table.comon)
pot = table.start_betting_round()
table.pot += pot
print(f"Pot: {table.pot}")

# Mostrar estado antes del showdown
print("\n--- Estado antes del showdown ---")
for p in players:
    print(f"{p.name}: stack={p.stack}, bet={p.current_bet}, in_game={p.in_game}")

# Resolver ganador
resultados = table.resolve_winner()

# Mostrar ganadores
print("\n--- Ganadores ---")
for winners, pot in resultados:
    names = ", ".join(w.name for w in winners)
    print(f"{names} gana {pot} fichas")

# Mostrar stacks finales
print("\n--- Stacks finales ---")
for p in players:
    print(f"{p.name}: stack={p.stack}")
