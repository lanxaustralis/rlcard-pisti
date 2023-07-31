'''
    File name: pisti/pisti_dealer.py
    Author: Yusa Omer Altintop
    Date created: 25/7/2023
'''
from typing import List

from rlcard.games.pisti.pisti_player import PistiPlayer
from rlcard.games.pisti.pisti_card import PistiCard


class PistiDealer:
    ''' Initialize a BridgeDealer dealer class
    '''
    def __init__(self, np_random, init_card_num=4):
        ''' set shuffled_deck, set stock_pile
        '''
        self.np_random = np_random
        self.init_card_num = init_card_num

        self.original_shuffled_deck: List[PistiCard] = PistiCard.get_deck()
        self.np_random.shuffle(self.original_shuffled_deck)

        self.secret_initial_deck: List[PistiCard] = self.original_shuffled_deck.copy()[:init_card_num-1]
        self.current_stock_pile: List[PistiCard] = self.original_shuffled_deck.copy()[init_card_num-1:init_card_num]
        self.remaining_deck: List[PistiCard] = self.original_shuffled_deck.copy()[init_card_num:]

        self.is_over = False

    def deal_cards(self, player: PistiPlayer, num: int = 4):
        if len(self.remaining_deck) == 0:
            self.is_over = True
            # print('No cards to deal!')
        else:
            for _ in range(num):
                player.hand.append(self.remaining_deck.pop(0))
            # self.remaining_deck = self.remaining_deck[num:]


