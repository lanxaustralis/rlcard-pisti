from collections import OrderedDict

import numpy as np

from rlcard.envs import Env
from rlcard.games.pisti import Game

from rlcard.games.pisti.pisti_utils import cards2list

DEFAULT_GAME_CONFIG = {
        'game_num_players': 2,
        'allow_step_back': False,
        'seed': None,
        'playing_with_human': False,
        'agent_level': 'hard'
        }


class PistiEnv(Env):

    def __init__(self, config=None):
        self.name = 'pisti'
        self.default_game_config = DEFAULT_GAME_CONFIG


        if config is None:
            config = DEFAULT_GAME_CONFIG

        self.game = Game(playing_with_human=config['playing_with_human'])
        super().__init__(config)

        self.agent_level = config['agent_level']

        if self.agent_level == 'easy':
            self.state_shape = [[1, 208] for _ in range(self.num_players)]
        elif self.agent_level == 'medium':
            self.state_shape = [[self.num_players, 211] for _ in range(self.num_players)]
        elif self.agent_level == 'hard':
            self.state_shape = [[self.num_players, 315] for _ in range(self.num_players)]
        else:
            raise ValueError("Agent level must be either of the following: easy, medium, hard")
        self.action_shape = [[52] for _ in range(self.num_players)]



    def get_payoffs(self):

        return np.array(self.game.get_all_payoffs())

    def _decode_action(self, action_id):
        legal_ids = self._get_legal_actions()
        if action_id not in legal_ids:
            action_id = np.random.choice(legal_ids)
        original_stock = self.game.dealer.original_shuffled_deck
        for card in original_stock:
            if action_id == card.card_numeric_id:
                return card
        return None

    def _get_legal_actions(self):
        legal_actions = self.game.get_legal_actions()
        legal_ids = {action.card_numeric_id: action.card_str_id for action in legal_actions}
        return OrderedDict(legal_ids)

    def get_perfect_information(self):
        ''' Get the perfect information of the current state

        Returns:
            (dict): A dictionary of all the perfect information of the current state
        '''
        state = {}
        state['num_players'] = self.num_players
        state['hand_cards'] = [cards2list(player.hand)
                               for player in self.game.players]
        state['played_cards'] = cards2list(self.game.round.played_cards)
        state['current_player'] = self.game.round.current_player
        state['legal_actions'] = self.game.round.get_legal_actions(
            self.game.players, state['current_player'])
        return state

    def _extract_state(self, state):
        ''' Extract useful information from state for RL.

        Args:
            game (BridgeGame): The game

        Returns:
            (numpy.array): The extracted state
        '''
        num_players = self.default_game_config['game_num_players']

        game = self.game
        extracted_state = {}

        legal_actions = self._get_legal_actions()
        raw_legal_actions = np.ones(52, dtype=int)

        current_player_id = game.get_player_id()

        rep = []

        # Universal Info

        # 1 - Construct Dealer Related Information
        ## Construct curr_stock_rep for current stockpile of cards
        curr_stock_rep = np.zeros(shape=(1,52), dtype=int)
        if not game.is_over():
            for card in game.dealer.current_stock_pile:
                curr_stock_rep[0][card.card_numeric_id] = 1

        ## Construct top_card_rep for top card on the stack
        top_card_rep = np.zeros(shape=(1,52), dtype=int)
        if not game.is_over():
            current_stock = game.dealer.current_stock_pile
            if len(current_stock) != 0:
                card = current_stock[-1]
                top_card_rep[0][card.card_numeric_id] = 1

        # 2 - Construct Universal Player Information
        # Construct current_player_rep for who is the current player
        current_player_rep = np.zeros(shape=(num_players, 1), dtype=int)
        if not game.is_over():
            current_player_rep[current_player_id] = 1

        # Construct player_scores_rep for current scores of the player
        player_scores_rep = np.zeros(shape=(num_players, 1), dtype=int)
        for player in self.game.players:
            player_scores_rep[player.get_player_id()] = player.get_score()

        # Construct collected_cards_rep for number of the collected cards of the player
        collected_cards_rep = np.zeros(shape=(num_players, 1), dtype=int)
        for player in self.game.players:
            collected_cards_rep[player.get_player_id()] = player.get_collected_num()


        if self.agent_level == 'easy':
            # 1 - Construct Player Related Information
            ## Construct hands_rep for hands of players
            curr_player = game.players[current_player_id]
            hands_rep = np.zeros(shape=(1,52), dtype=int)
            if not game.is_over():
                for card in curr_player.hand:
                    hands_rep[0][card.card_numeric_id] = 1

            ## Construct seen_rep for seen cards of players
            seen_rep = np.zeros(shape=(1,52), dtype=int)
            if not game.is_over():
                for seen_card in curr_player.seen_cards:
                    seen_rep[0][seen_card.card_numeric_id] = 1

            rep = [hands_rep, seen_rep, curr_stock_rep, top_card_rep]

        else:
            # 1 - Construct Player Related Information
            ## Construct hands_rep for hands of players
            hands_rep = np.zeros(shape=(num_players, 52), dtype=int)
            if not game.is_over():
                for player in game.players:
                    player_id = player.get_player_id()
                    for card in game.players[player_id].hand:
                        hands_rep[player_id][card.card_numeric_id] = 1

            ## Construct seen_rep for seen cards of players
            seen_rep = np.zeros(shape=(num_players, 52), dtype=int)
            if not game.is_over():
                for player in game.players:
                    player_id = player.get_player_id()
                    for seen_card in game.players[player_id].seen_cards:
                        seen_rep[player_id][seen_card.card_numeric_id] = 1

            # 2 - Construct Dealer Related Information
            ## Combine curr_stock_rep to achieve desired size
            cumulative_curr_stock_rep = curr_stock_rep
            for _ in range(self.num_players-1):
                cumulative_curr_stock_rep = np.vstack((cumulative_curr_stock_rep, curr_stock_rep))

            ## Combine top_card_rep to achieve desired size
            cumulative_top_card_rep = top_card_rep
            for _ in range(self.num_players-1):
                cumulative_top_card_rep = np.vstack((cumulative_top_card_rep, top_card_rep))


            rep = [hands_rep, seen_rep, cumulative_curr_stock_rep, cumulative_top_card_rep, current_player_rep, player_scores_rep, collected_cards_rep]

            if self.agent_level == 'hard':
                # Including Future Information
                next_hands_rep = np.zeros(shape=(num_players, 52), dtype=int)
                if not game.is_over():
                    rem_deck = game.dealer.remaining_deck
                    if len(rem_deck)!=0:
                        for player in game.players:
                            player_id = player.get_player_id()
                            next_hand = rem_deck[:game.deal_per_round]
                            rem_deck = rem_deck[game.deal_per_round:]
                            for card in next_hand:
                                next_hands_rep[player_id][card.card_numeric_id] = 1

                # Including Secret Information
                initial_secret_rep = np.zeros(shape=(num_players, 52), dtype=int)
                if not game.is_over():
                    initial_secret = game.dealer.secret_initial_deck
                    if len(initial_secret)!=0:
                        for player in game.players:
                            player_id = player.get_player_id()
                            for card in initial_secret:
                                initial_secret_rep[player_id][card.card_numeric_id] = 1

                rep.append(next_hands_rep)
                rep.append(initial_secret_rep)


        obs = np.hstack(rep)
        extracted_state['obs'] = obs
        extracted_state['legal_actions'] = legal_actions
        extracted_state['raw_legal_actions'] = raw_legal_actions
        extracted_state['raw_obs'] = obs
        extracted_state['human_req_info'] = self.game.get_all_states()

        return extracted_state
