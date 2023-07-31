'''
    File name: pisti/pisti_game.py
    Author: Yusa Omer Altintop
    Date created: 25/7/2023
'''

from copy import deepcopy
import numpy as np

from rlcard.games.pisti.pisti_round import PistiRound
from rlcard.games.pisti.pisti_judger import PistiJudger
from rlcard.games.pisti.pisti_player import PistiPlayer
from rlcard.games.pisti.pisti_dealer import PistiDealer


class PistiGame:
    ''' Game class. This class will interact with outer environment.
    '''

    def __init__(self, allow_step_back=False, num_players=2, num_init_cards=4, deal_per_round=4,
                 playing_with_human=False):

        self.allow_step_back: bool = allow_step_back
        self.np_random = np.random.RandomState()
        self.num_players = num_players
        self.num_init_cards = num_init_cards
        self.deal_per_round = deal_per_round
        self.playing_with_human = playing_with_human

    def configure(self, game_config):
        ''' Specifiy some game specific parameters, such as number of players
        '''
        self.num_players = game_config['game_num_players']

    def init_game(self):
        ''' Initialize players and state

        Returns:
            (tuple): Tuple containing:

                (dict): The first state in one game
                (int): Current player's id
        '''
        # Initalize payoffs
        self.payoffs = [0 for _ in range(self.num_players)]

        # Initialize a dealer that can deal cards
        self.dealer = PistiDealer(self.np_random)

        # Initialize four players to play the game
        self.players = [PistiPlayer(i, self.np_random) for i in range(self.num_players)]

        # Deal cards to each player to prepare for the game
        for player in self.players:
            self.dealer.deal_cards(player, self.deal_per_round)

        # Initialize a Round
        self.round = PistiRound(self.dealer, self.np_random, self.num_players, self.num_init_cards, self.deal_per_round)

        # Save the hisory for stepping back to the last state.
        self.history = []

        current_player_id = self.get_player_id()
        state = self.get_state_for_player(current_player_id)

        if self.playing_with_human:
            print(f'The top card of the deck is {self.dealer.current_stock_pile[-1]}')

        return state, current_player_id

    def step(self, action):
        ''' Get the next state

        Args:
            action (str): A specific action

        Returns:
            (tuple): Tuple containing:

                (dict): next player's state
                (int): next plater's id
        '''

        if self.allow_step_back:
            # First snapshot the current state
            his_dealer = deepcopy(self.dealer)
            his_round = deepcopy(self.round)
            his_players = deepcopy(self.players)
            self.history.append((his_dealer, his_players, his_round))

        self.round.proceed_round(self.players, action, playing_with_human=self.playing_with_human)
        player_id = self.round.current_player_id
        state = self.get_state_for_player(player_id)
        return state, player_id

    def step_back(self):
        ''' Return to the previous state of the game

        Returns:
            (bool): True if the game steps back successfully
        '''
        if not self.history:
            return False
        self.dealer, self.players, self.round = self.history.pop()
        return True

    def get_num_players(self) -> int:
        ''' Return the number of players in the game
        '''
        return self.num_players

    def get_legal_actions(self):
        ''' Return the legal actions for current player

        Returns:
            (list): A list of legal actions
        '''

        return self.round.get_legal_actions_for_current_player(self.players, self.playing_with_human)

    def get_state_for_player(self, player_id=-1):  # wch: not really used
        ''' Get player's state

        Return:
            state (dict): The information of the state
        '''
        if player_id == -1:
            player_id = self.get_player_id()
        state = self.round.get_state_for_current_player(self.players, player_id)
        state['num_players'] = self.get_num_players()

        return state

    def get_state(self, player_id):
        return self.get_state_for_player(player_id)

    @staticmethod
    def get_num_actions():
        ''' Return the number of applicable actions

        Returns:
            (int): The number of actions. There are 52 actions each for one card
        '''
        return 52

    def get_player_id(self):
        ''' Return the current player's id

        Returns:
            (int): current player's id
        '''
        return self.round.current_player_id

    def is_over(self):
        ''' Check if the game is over

        Returns:
            (boolean): True if the game is over
        '''
        return self.round.is_over

    def get_all_states(self):  # wch: not really used
        ''' Get player's state

        Return:
            state (dict): The information of the state
        '''
        state = {'num_players': self.get_num_players()}
        for player in self.players:
            player_id = player.get_player_id()
            state[player_id] = self.round.get_state_for_current_player(self.players, player.get_player_id())

        return state

    def get_all_payoffs(self):
        ''' Return the payoffs of the game

        Returns:
            (list): Each entry corresponds to the payoff of one player
        '''
        if self.round.is_over:
            return PistiJudger.judge_winner_score(self.players)
        else:
            return PistiJudger.judge_current_score(self.players)
