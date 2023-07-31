'''
    File name: pisti/pisti_judger.py
    Author: Yusa Omer Altintop
    Date created: 25/7/2023
'''


class PistiJudger:

    @staticmethod
    def judge_current_score(players):
        scores = {}
        for player in players:
            scores[player.get_player_id()] = player.get_score()
        return list(scores.values())

    @staticmethod
    def judge_winner_score(players):
        scores = {}
        max_collected_cards = -1
        max_collector = -1
        for player in players:
            player_score = player.get_score()
            player_collected = player.get_collected_num()
            if max_collected_cards < player_collected:
                max_collected_cards = player_collected
                max_collector = player.get_player_id()
            scores[player.get_player_id()] = player_score
        scores[max_collector] += 3

        return list(scores.values())
