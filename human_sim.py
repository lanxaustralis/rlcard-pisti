import rlcard
from rlcard.agents.human_agents.pisti_human_agent import HumanAgent
from rlcard.agents import NFSPAgent
import torch

agent_levels = {0: 'easy',
                1: 'medium',
                2: 'hard'}

print(f'>> Please decide the bot level - 0: easy, 1: medium, 2: hard: ')

bot_level = int(input())

while bot_level < 0 or bot_level >= 3:
    print('Action illegal...')
    bot_level = int(input('>> Re-choose bot level - 0: easy, 1: medium, 2: hard: '))

agent_level = agent_levels[bot_level]
agent_dir = f'trained_pisti_models/model_nfsp_{agent_level}.pth'

# Make environment
env_name = 'pisti'
seed = 42

env = rlcard.make('pisti', config={'seed': seed,'playing_with_human':True, 'agent_level': agent_level})
human_agent = HumanAgent(env.num_actions, print_pretty=True)
nfsp_agent = torch.load(agent_dir)

env.set_agents([
    nfsp_agent,
    human_agent,

])


print(">> Pisti rule model V1")
continue_game = 1

while (continue_game):
    print(">> Start a new game")

    trajectories, payoffs = env.run(is_training=False)
    # If the human does not take the final action, we need to
    # print other players action
    final_state = trajectories[0][-1]

    print('===============     Result     ===============')
    human_score = payoffs[0]
    agent_score = payoffs[1]
    
    print(f'Your score is {human_score}, agent score is {agent_score}')
    
    if human_score > agent_score:
        print('You win!')
    else:
        print('You lose!')

    print(f'Press {1} to continue, press {0} to abort')
    continue_game = int(input())