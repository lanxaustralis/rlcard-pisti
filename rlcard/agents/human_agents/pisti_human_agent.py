from rlcard.games.pisti.pisti_utils import print_card
from rlcard.games.pisti.pisti_card import PistiCard
from typing import List


class HumanAgent(object):
    ''' A human agent for Blackjack. It can be used to play alone for understand how the blackjack code runs
    '''

    def __init__(self, num_actions, print_pretty=False):
        ''' Initilize the human agent

        Args:
            num_actions (int): the size of the output action space
        '''
        self.use_raw = True
        self.num_actions = num_actions
        self.print_pretty = print_pretty

    def step(self, state):
        ''' Human agent will display the state and make decisions through interfaces

        Args:
            state (dict): A dictionary that represents the current state

        Returns:
            action (int): The action decided by human
        '''

        # _print_state(state['raw_obs'], state['legal_actions'])

        legal_actions = state['legal_actions'] # Ordered dict, no cards
        cards: List[PistiCard] = PistiCard.get_deck()

        last_card = state['human_req_info'][0]['last_card_on_deck']
        if last_card is not None:
            last_card = f'{last_card.suit} {last_card.rank}'
        hand = []
        for _, card_str in legal_actions.items():
            hand.append(card_str)

        if self.print_pretty:
            print('The last card on the deck is as follows: ')
            print_card([last_card])
            print('Your hand is as follows: ')
            print_card(hand)
        else:
            print('Your hand is as follows: ', end=' ')
            print(*hand, sep=' - ')

        print(f'>> Play a card (based on its position - a number between 0 and {len(legal_actions) - 1}): ')
        action_index = int(input())

        while action_index < 0 or action_index >= len(legal_actions):
            print('Action illegal...')
            action_index = int(input('>> Re-choose action (integer): '))

        card_info = list(legal_actions.items())[action_index]

        for card in cards:
            if card.card_numeric_id == card_info[0]:
                return card

        return None

    def eval_step(self, state):
        ''' Predict the action given the current state for evaluation. The same to step here.

        Args:
            state (numpy.array): an numpy array that represents the current state

        Returns:
            action (int): the action predicted (randomly chosen) by the random agent
        '''
        return self.step(state), {}

