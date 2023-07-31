'''
    File name: pisti/pisti_round.py
    Author: Yusa Omer Altintop
    Date created: 25/7/2023
'''

from typing import List
from rlcard.games.pisti.pisti_player import PistiPlayer
from rlcard.games.pisti.pisti_dealer import PistiDealer
from rlcard.games.pisti.pisti_utils import cards2list
from rlcard.games.pisti.pisti_judger import PistiJudger
from rlcard.games.pisti.pisti_card import PistiCard


class PistiRound:

    def __init__(self, dealer: PistiDealer, np_random, num_players=2, num_init_cards=4, deal_per_round=4):
        ''' Initialize the round class

        Args:
            dealer (object): the object of UnoDealer
            num_players (int): the number of players in game
        '''
        self.dealer = dealer
        self.np_random = np_random
        self.num_players = num_players
        self.num_init_cards = num_init_cards
        self.deal_per_round = deal_per_round

        self.target = None
        self.current_player_id: int = 0

        self.is_over = False
        self.winner = None

        self.initial_secret: List[PistiCard] = self.dealer.secret_initial_deck
        self.universal_seen_cards: List[PistiCard] = self.dealer.current_stock_pile # initially this contains only one card

        self.last_collector = -1

    def proceed_round(self, players: List[PistiPlayer], action: PistiCard, playing_with_human=False):
        initial_secret = self.initial_secret
        cards_on_stock = self.dealer.current_stock_pile



        curr_player = players[self.current_player_id]
        curr_stock = curr_player.play_card(cards_on_stock=cards_on_stock, to_be_played=action,
                                           initial_secret=initial_secret, playing_with_human=playing_with_human)

        for player in players:
            player.update_seen_cards(action)

        if len(curr_stock) == 0 and len(initial_secret) != 0:
            for secret_card in initial_secret:
                curr_player.update_seen_cards(secret_card)
            self.initial_secret = []

        if len(curr_stock) == 0:
            self.last_collector = self.current_player_id

        if len(self.dealer.remaining_deck) == 0:
            if len(curr_player.hand) == 0:
                if self.current_player_id == (self.num_players - 1):
                    if len(curr_stock) != 0:
                        players[self.last_collector].collect_cards(curr_stock, playing_with_human=False)
                        if playing_with_human:
                            print(f'{self.last_collector} collected all the remaining cards as the last collector!')


        self.dealer.current_stock_pile = curr_stock
        self.current_player_id = (self.current_player_id + 1) % self.num_players

    def get_legal_actions_for_current_player(self, players, playing_with_human=False):
        curr_player: PistiPlayer = players[self.current_player_id]
        curr_hand = curr_player.hand

        if len(curr_hand) == 0:
            if not self.dealer.is_over:
                for player in players:
                    self.dealer.deal_cards(player, num=self.deal_per_round)
                curr_hand = players[self.current_player_id].hand
            else:
                self.is_over = self.dealer.is_over
        legal_actions = curr_hand

        return legal_actions

    def get_state_for_current_player(self, players, player_id=-1):
        state = {}
        if player_id == -1:
            player_id = self.current_player_id
        player: PistiPlayer = players[player_id]
        state['hand'] = cards2list(player.hand)
        state['seen_cards'] = cards2list(player.seen_cards)
        state['collected_num'] = player.get_collected_num()
        state['player_score'] = player.get_score()
        state['legal_actions'] = self.get_legal_actions_for_current_player(players)
        state['scores'] = PistiJudger.judge_current_score(players)
        state['current_player'] = self.current_player_id

        state['num_cards'] = []
        for player in players:
            state['num_cards'].append(len(player.hand))

        last_card = None
        if len(self.dealer.current_stock_pile) != 0:
            last_card = self.dealer.current_stock_pile[-1]
        state['last_card_on_deck'] = last_card
        return state
