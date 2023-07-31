'''
    File name: pisti/pisti_player.py
    Author: Yusa Omer Altintop
    Date created: 25/7/2023
'''

from typing import List
from rlcard.games.pisti.pisti_card import PistiCard


class PistiPlayer:

    def __init__(self, player_id: int, np_random):
        self.np_random = np_random
        self.player_id: int = player_id

        self.hand: List[PistiCard] = []
        self.seen_cards: List[PistiCard] = []

        self.score = 0
        self.collected_num = 0

    def play_card_from_hand(self, card: PistiCard, playing_with_human=False):
        if playing_with_human:
            print(f'Player {self.player_id} played {card}!')
        self.hand.remove(card)

    def collect_cards(self, cards_on_stock: List[PistiCard], playing_with_human=False):
        last_card: PistiCard = cards_on_stock[-1]
        if len(cards_on_stock) == 2:  # it means pisti
            if cards_on_stock[-2].equal_ranks(cards_on_stock[-1]):
                if playing_with_human:
                    print(f'Player {self.player_id} made pisti by playing {last_card}!')
                if last_card.is_joker():
                    self.score += 20
                else:
                    self.score += 10
        if playing_with_human:
            print(f'Player {self.player_id} collected all cards by playing {last_card}!')
        for card in cards_on_stock:
            self.score += card.get_point()

        self.collected_num += len(cards_on_stock)
        if playing_with_human:
            print(
                f'Player {self.player_id} collected {self.collected_num} cards in total')

    def play_card(self, cards_on_stock: List[PistiCard], to_be_played: PistiCard, initial_secret: List[PistiCard],
                  playing_with_human=False):
        self.play_card_from_hand(to_be_played, playing_with_human)
        cards_on_stock.append(to_be_played)
        if len(cards_on_stock) != 1:
            if cards_on_stock[-2].equal_ranks(cards_on_stock[-1]) or cards_on_stock[-1].is_joker():
                if len(initial_secret) != 0:
                    initial_secret.extend(cards_on_stock)
                    cards_on_stock = initial_secret
                self.collect_cards(cards_on_stock, playing_with_human)
                empty_stock: List[PistiCard] = []
                return empty_stock
        return cards_on_stock

    def update_seen_cards(self, card: PistiCard):
        self.seen_cards.append(card)

    def get_score(self):
        return self.score

    def get_player_id(self):
        return self.player_id

    def get_collected_num(self):
        return self.collected_num

    def __str__(self):
        return f'Player {self.player_id}'

    def print_player_stats(self):
        return f'Player ID: {self.player_id} \nHand: {self.hand} \nCollected Cards: {self.score}'
