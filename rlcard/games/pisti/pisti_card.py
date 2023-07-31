'''
    File name: pisti/pisti_card.py
    Author: Yusa Omer Altintop
    Date created: 25/7/2023
'''


class PistiCard:
    suits = ['CLUBS', 'HEARTS', 'SPADES', 'DIAMONDS']
    ranks = ['ACE', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

    @staticmethod
    def card(card_id: int):
        return _deck[card_id]

    @staticmethod
    def get_deck():
        return _deck.copy()

    def __init__(self, suit: str, rank: str):
        self.suit = suit
        self.rank = rank

        suit_index = PistiCard.suits.index(self.suit)
        rank_index = PistiCard.ranks.index(self.rank)

        self.card_numeric_id = 13 * suit_index + rank_index
        self.card_str_id = f'{self.suit} {self.rank}'

        self.point = 0
        self.assign_card_point()

    def assign_card_point(self):
        suit = self.suit
        rank = self.rank

        if rank == 'ACE' or rank == 'J':
            self.point = 1
        elif suit == 'CLUBS' and rank == '2':
            self.point = 2
        elif suit == 'DIAMONDS' and rank == '10':
            self.point = 3

    def get_index(self, is_numeric=False):
        if is_numeric:
            return self.card_numeric_id
        return self.card_str_id

    def get_point(self):
        return self.point

    def equal_ranks(self, other):
        if isinstance(other, PistiCard):
            return self.rank == other.rank
        else:
            # don't attempt to compare against unrelated types
            return NotImplemented

    def is_joker(self):
        return self.rank == 'J'

    def __str__(self):
        return f'{self.card_str_id}'

    def __repr__(self):
        return f'{self.card_str_id}'

    def __eq__(self, other):
        if isinstance(other, PistiCard):
            return self.rank == other.rank and self.suit == other.suit
        else:
            # don't attempt to compare against unrelated types
            return NotImplemented

    def __hash__(self):
        suit_index = PistiCard.suits.index(self.suit)
        rank_index = PistiCard.ranks.index(self.rank)
        return 100 * suit_index + rank_index


_deck = [PistiCard(suit=suit, rank=rank) for suit in PistiCard.suits for rank in PistiCard.ranks]
