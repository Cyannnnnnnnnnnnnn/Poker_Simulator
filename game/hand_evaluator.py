from itertools import combinations
from collections import Counter
from functools import total_ordering

values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
          '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}

ranking = {
    'Straight flush': 9,
    'Poker': 8,
    'Full house': 7,
    'Flush': 6,
    'Straight': 5,
    'Set': 4,
    'Double pair': 3,
    'Pair': 2,
    'High': 1
}

@total_ordering
class EvaluatedHand:
    def __init__(self, type, cards, kickers):
        self.type = type
        self.ranking = ranking[type]
        self.cards = sorted(cards, key=lambda c: values[c.value], reverse=True)
        self.kickers = sorted(kickers, key=lambda c: values[c.value], reverse=True)

    def compare_with(self, other):
        if self.ranking > other.ranking:
            return 1
        elif self.ranking < other.ranking:
            return -1
        for a, b in zip(self.cards, other.cards):
            if values[a.value] > values[b.value]:
                return 1
            elif values[a.value] < values[b.value]:
                return -1
        for a, b in zip(self.kickers, other.kickers):
            if values[a.value] > values[b.value]:
                return 1
            elif values[a.value] < values[b.value]:
                return -1
        return 0

    def __eq__(self, other):
        return self.compare_with(other) == 0

    def __lt__(self, other):
        return self.compare_with(other) < 0

    def __str__(self):
        return f"{self.type} con {self.cards} y kickers {self.kickers}"

    def __repr__(self):
        return self.__str__()


class HandEvaluator:
    def get_strength_ratio(self, cards):
        if len(cards) < 5:
            return self._evaluate_preflop_strength(cards)
        best = self.evaluate_best_hand(cards)
        if best is None:
            return 0.0
        return best.ranking / 9

    def _evaluate_preflop_strength(self, hand):
        """Evalúa la fuerza de una mano de 2 cartas preflop. Devuelve un valor entre 0 y 1."""
        c1, c2 = hand
        v1, v2 = values[c1.value], values[c2.value]

        # Par
        if c1.value == c2.value:
            return v1 / 14  # Par de ases = 1.0

        # Mismo palo (suited)
        suited = c1.suit == c2.suit

        # Conectores (diferencia <= 1)
        gap = abs(v1 - v2)

        score = (v1 + v2) / 28  # suma máxima = 14+14 = 28
        if suited:
            score += 0.1
        if gap == 1:
            score += 0.05

        return min(score, 1.0)

    def evaluate_best_hand(self, cards):
        best = None
        for combo in combinations(cards, 5):
            result = self._evaluate_hand(combo)
            if best is None or result.compare_with(best) > 0:
                best = result
        return best

    def _evaluate_hand(self, five_cards):
        checkers = [
            self._straight_flush,
            self._four_of_a_kind,
            self._full_house,
            self._flush,
            self._straight,
            self._three_of_a_kind,
            self._two_pair,
            self._one_pair,
            self._high_card
        ]
        for check in checkers:
            result = check(five_cards)
            if result:
                return result
        return None

    def _straight_flush(self, cards):
        suits = [c.suit for c in cards]
        for suit in set(suits):
            same_suit = [c for c in cards if c.suit == suit]
            if len(same_suit) >= 5:
                result = self._straight(same_suit)
                if result:
                    return EvaluatedHand("Straight flush", result.cards, result.kickers)
        return None

    def _four_of_a_kind(self, cards):
        count = Counter(c.value for c in cards)
        for value, cnt in count.items():
            if cnt == 4:
                four = [c for c in cards if c.value == value]
                kickers = [c for c in cards if c.value != value]
                return EvaluatedHand("Poker", four, kickers[:1])
        return None

    def _full_house(self, cards):
        count = Counter(c.value for c in cards)
        three = [v for v in count if count[v] == 3]
        pairs = [v for v in count if count[v] == 2]
        if len(three) >= 2:
            # Usa uno como trio, otro como pareja
            trio_cards = [c for c in cards if c.value == three[0]]
            pair_cards = [c for c in cards if c.value == three[1]]
            return EvaluatedHand("Full house", trio_cards + pair_cards, [])
        elif len(three) == 1 and pairs:
            trio_cards = [c for c in cards if c.value == three[0]]
            pair_cards = [c for c in cards if c.value == pairs[0]]
            return EvaluatedHand("Full house", trio_cards + pair_cards, [])

        return None

    def _flush(self, cards):
        suits = [c.suit for c in cards]
        for suit in set(suits):
            suited = [c for c in cards if c.suit == suit]
            if len(suited) >= 5:
                return EvaluatedHand("Flush", sorted(suited, key=lambda c: values[c.value], reverse=True)[:5], [])
        return None

    def _straight(self, cards):
        unique_values = sorted(set(values[c.value] for c in cards), reverse=True)
        if 14 in unique_values:
            unique_values.append(1)  # A as 1 for A-2-3-4-5
        for i in range(len(unique_values) - 4):
            if unique_values[i] - unique_values[i+4] == 4:
                straight_vals = set(unique_values[i:i+5])
                straight_cards = sorted([c for c in cards if values[c.value] in straight_vals],
                                        key=lambda c: values[c.value], reverse=True)[:5]
                return EvaluatedHand("Straight", straight_cards, [])
        return None

    def _three_of_a_kind(self, cards):
        count = Counter(c.value for c in cards)
        for value, cnt in count.items():
            if cnt == 3:
                three = [c for c in cards if c.value == value]
                kickers = sorted([c for c in cards if c.value != value], key=lambda c: values[c.value], reverse=True)[:2]
                return EvaluatedHand("Set", three, kickers)
        return None

    def _two_pair(self, cards):
        count = Counter(c.value for c in cards)
        pairs = [v for v in count if count[v] >= 2]
        if len(pairs) >= 2:
            top2 = sorted(pairs, key=lambda x: values[x], reverse=True)[:2]
            pair_cards = [c for c in cards if c.value in top2]
            kicker = [c for c in cards if c.value not in top2]
            return EvaluatedHand("Double pair", pair_cards, kicker[:1])
        return None

    def _one_pair(self, cards):
        count = Counter(c.value for c in cards)
        for value, cnt in count.items():
            if cnt == 2:
                pair = [c for c in cards if c.value == value]
                kickers = sorted([c for c in cards if c.value != value], key=lambda c: values[c.value], reverse=True)[:3]
                return EvaluatedHand("Pair", pair, kickers)
        return None

    def _high_card(self, cards):
        ordered = sorted(cards, key=lambda c: values[c.value], reverse=True)
        return EvaluatedHand("High", [ordered[0]], ordered[1:])

