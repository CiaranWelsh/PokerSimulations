import sqlite3
import os, glob
import zipfile
import re
from datetime import datetime
from collections import OrderedDict

from . import file_manager

FILE_MANAGER = file_manager.FileManager()


class Zipper:
    @staticmethod
    def get_zip_files(directory):
        return glob.glob(os.path.join(directory, '*.zip'))

    @staticmethod
    def unzip(f, replace=False):
        if not os.path.isfile(f):
            raise FileNotFoundError(f)

        with zipfile.ZipFile(f, "r") as zip_ref:
            zip_ref.extractall(f[:-4])

    def extract(self):
        files = self.get_zip_files(FILE_MANAGER.MICRO_STAKES_DIR)
        for f in files:
            self.unzip(f)


class HandParser:
    _re_game_id = r'#Game No : (\d*)'
    _re_steaks = r'\$(\d*.\d*)\/\$(\d*.\d*)'
    _re_button = r'Seat (\d*) is the button'
    _re_datetime = r'Blinds No Limit Holdem .* \*\*\* (\d{2}) (\d{2}) (\d{4}) (\d{2}):(\d{2}):(\d{2})'
    _re_number_of_players = 'Total number of players : (\d*)'
    _re_player_info = r'Seat (\d*): (\w*) \( \$(\d*\.\d*) \)'
    _re_preflop_actions = r'\*\* Dealing down cards \*\*\n[\s\S]*\*\* Dealing flop \*\*'
    _re_flop_actions = r'\*\* Dealing flop \*\* .* [\s\S]*\* Dealing turn \*\*'
    _re_turn_actions = r'\*\* Dealing turn \*\* .*[\s\S]*\*\* Dealing river \*\*'
    _re_river_actions = r'\*\* Dealing river \*\* .*[\s\S]*\*\* Summary \*\*'
    _re_flop = r'\*\* Dealing flop \*\* (.*)'
    _re_turn = r'\*\* Dealing turn \*\* (.*)'
    _re_river = r'\*\* Dealing river \*\* (.*)'
    _re_summary = r'\*\* Summary \*\*[\s\S]*'
    _re_winner = r'(\w*) collected.*\$(\d*.\d*).*'

    def __init__(self, hand):
        self.hand = hand

    # @staticmethod
    # def from_file(file):
    #     if not os.path.isfile(file):
    #         raise FileNotFoundError
    #
    #     with open(file, 'r') as fh:
    #         text = fh.read()
    #
    #     return Hand(text.split('\n\n'))

    def parse_hand(self):
        pass

    def game_id(self):
        id = re.findall(self._re_game_id, self.hand)[0]
        return int(id)

    def steaks(self):
        steaks = re.findall(self._re_steaks, self.hand)[0]
        return float(steaks[0]), float(steaks[1])

    def button(self):
        btn = re.findall(self._re_button, self.hand)[0]
        return int(btn)

    def number_of_players(self):
        players = re.findall(self._re_number_of_players, self.hand)[0]
        return int(players)

    def player_info(self):
        seats = re.findall(self._re_player_info, self.hand)
        return {int(i): {j: float(k)} for (i, j, k) in seats}

    def _get_actions(self, regex):
        """
        method for retrieving a set of actions
        :param regex:
        :return:
        """
        actions = re.findall(regex, self.hand)[0]
        actions = actions.split('\n')[1:-1]
        dct = OrderedDict()
        for action in actions:
            amount = None
            tmp = action.split(' ')
            if len(tmp) == 3:
                player, act, amount = tmp
                amount = float(amount[2:-1])
            else:
                player, act = tmp

            dct[player] = (act, None if amount is None else amount)

        return dct

    def flop(self):
        flop = re.findall(self._re_flop, self.hand)[0]
        flop = flop.replace('[', '').replace(']', '').replace(' ', '').split(',')
        return flop

    def preflop_actions(self):
        return self._get_actions(self._re_preflop_actions)

    def flop_actions(self):
        return self._get_actions(self._re_flop_actions)

    def turn(self):
        turn = re.findall(self._re_turn, self.hand)[0]
        turn = turn.replace(' ', '').replace('[', '').replace(']', '')
        return turn

    def turn_actions(self):
        return self._get_actions(self._re_turn_actions)

    def river(self):
        river = re.findall(self._re_river, self.hand)[0]
        river = river.replace(' ', '').replace('[', '').replace(']', '')
        return river

    def river_actions(self):
        return self._get_actions(self._re_river_actions)

    def showdown(self):
        summary = re.findall(self._re_summary, self.hand)[0]
        summary = summary.split('\n')[1:-1]
        summary = [i.replace('[', '').replace(']', '') for i in summary]
        dct = OrderedDict()
        for i in summary:
            player, action, cards = re.findall('(\w*) (\w*) (.*)', i)[0]
            cards = cards.replace(' ', '').split(',')
            dct[player] = (action, cards)
        return dct

    def winner(self):
        winner = re.findall(self._re_winner, self.hand)[0]
        return {'player': winner[0], 'cash': float(winner[1])}



