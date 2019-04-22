import os, glob
import numpy, pandas
from collections import OrderedDict
import re
import datetime


class PokerStarsParser:
    _valid_game_types = {
        1: ['preflop', 'summary'],
        2: ['preflop', 'flop', 'summary'],
        3: ['preflop', 'flop', 'turn', 'summary'],
        4: ['preflop', 'flop', 'turn', 'river', 'summary'],
        5: ['preflop', 'flop', 'turn', 'river', 'showdown', 'summary'],
    }
    ## problem: conditiion 4 is satisified both when fold at river and
    ## when we see showdown
    _re_vendor = 'PokerStars'
    _re_game_id = r'PokerStars Hand #(\d*)'
    _re_table_name = r"Table '(\w*)'"
    _re_steaks = r"Hold'em No Limit \(\$(\d*.\d*)\/\$(\d*.\d*) USD\)"
    _re_datetime = r"Hold'em No Limit .* - (.*) "
    _re_button = r"Table '\w*'.*Seat #(\d*) is the button"
    _re_number_of_players = '(\d*)-max'
    _re_head_data = "Table[(\s\S)]*\*\*\* HOLE CARDS \*\*\*"
    _re_player_info = "Seat (\d*): (.*) \(\$([\d.]*)"
    # _re_preflop_actions = r'\*\*\* HOLE CARDS \*\*\*[\s\S]*\*\*\*'
    _re_preflop_actions = r'\*\*\* HOLE CARDS \*\*\*[\s\S]*?\*\*\* (?:FLOP|SUMMARY)'
    _re_flop_actions = r'\*\*\* FLOP \*\*\*[\s\S]*?\*\*\* (?:TURN|SUMMARY)'
    _re_turn_actions = r'\*\*\* TURN \*\*\*[\s\S]*?\*\*\* (?:RIVER|SUMMARY)'
    _re_river_actions = r'\*\*\* RIVER \*\*\*[\s\S]*?\*\*\* SUMMARY'
    _re_showdown = r'\*\*\* SHOW DOWN \*\*\*[\s\S]*?\*\*\*'
    _re_summary = r'\*\*\* SUMMARY[\S\s]*'
    _re_flop = r'\*\*\* FLOP \*\*\*(.*)'
    _re_turn = r'\*\*\* TURN \*\*\* \[.*\].*\[(.*)\]'
    _re_river = r'\*\*\* RIVER \*\*\* \[.*\].*\[(.*)\]'
    _re_winner = r'(\w*) collected.*\$(\d*.\d*).*'

    def __init__(self, hand):
        self.hand = hand
        self.game_type = self._game_type()

    def _game_type(self):
        flop = False
        turn = False
        river = False
        showdown = False

        if re.findall(r'\*\*\* FLOP', self.hand) != []:
            flop = True

        if re.findall(r'\*\*\* TURN', self.hand) != []:
            turn = True

        if re.findall(r'\*\*\* RIVER', self.hand) != []:
            river = True

        if re.findall(r'\*\*\* SHOW DOWN', self.hand) != []:
            showdown = True

        if showdown and flop and turn and river:
            return 5
        elif flop and turn and river:
            return 4
        elif flop and turn and not river:
            return 3
        elif flop and not turn and not river:
            return 2
        elif not flop and not turn and not river:
            return 1

    def parse_hand(self):
        pass

    def datetime(self):
        return re.findall(self._re_datetime, self.hand)[0]

    def vendor(self):
        return re.findall(self._re_vendor, self.hand)[0]

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
        info = re.findall(self._re_head_data, self.hand)[0]
        info = info.split('\n')[1:-3]  # remove first and last few lines
        dct = OrderedDict()
        for i in info:
            seat, player, cash = re.findall(self._re_player_info, i)[0]
            seat = int(seat)
            cash = float(cash)
            dct[seat] = (player, cash)
        return dct

    def _get_actions(self, regex):
        """
        method for retrieving a set of actions
        :param regex:
        :return:
        """
        actions = re.findall(regex, self.hand)
        if len(actions) != 1:
            raise ValueError('regex has matched more than 1 item. Problem. ')
        actions = actions[0]
        actions = actions.split('\n')[1:-1]
        l = []
        for action in actions:
            player = re.findall('(\w*).', action)[0].strip()
            act = re.findall('(calls)|(disconnected)|(timed out)|'
                             '(raises)|(checks)|(folds)|(bets)', action)
            act = [i for i in act[0] if i != ''][0]
            ##default for check and fold
            amount = pot = None
            if act == 'raises':
                amount, pot = re.findall('\$(\d*.\d*) to \$(\d*.\d*)',
                                         action)[0]
                amount = float(amount)
                pot = float(pot)

            elif act in ['calls', 'bets']:
                amount = re.findall('\$(\d*.\d*)', action)[0]


            elif act in ['folds', 'checks', 'timed out',
                         'disconnected']:
                pass

            else:
                raise ValueError(f'"{act}" action has not been accounted for')

            l.append({'player': player, 'action': act, 'amount': amount, 'pot': pot})

        return l

    def flop(self):
        if self.game_type >= 2:
            flop = re.findall(self._re_flop, self.hand)[0]
            flop = flop.replace('[', '').replace(']', '').strip().replace(' ', ',').split(',')
            return flop
        else:
            return False

    def preflop_actions(self):
        return self._get_actions(self._re_preflop_actions)

    def flop_actions(self):
        return self._get_actions(self._re_flop_actions)

    def turn(self):
        if self.game_type >= 3:
            turn = re.findall(self._re_turn, self.hand)[0]
            turn = turn.replace(' ', '').replace('[', '').replace(']', '')
            return turn
        else:
            return False

    def turn_actions(self):
        if self.game_type >= 3:
            return self._get_actions(self._re_turn_actions)
        else:
            return False

    def river(self):
        if self.game_type == 4:
            river = re.findall(self._re_river, self.hand)[0]
            river = river.replace(' ', '').replace('[', '').replace(']', '')
            return river
        else:
            return False

    def river_actions(self):
        if self.game_type == 4:
            return self._get_actions(self._re_river_actions)
        else:
            return False

    def showdown(self):
        if self.game_type == 5:
            summary = re.findall(self._re_summary, self.hand)[0]
            summary = summary.split('\n')[1:-1]
            summary = [i.replace('[', '').replace(']', '') for i in summary]
            dct = OrderedDict()
            for i in summary:
                player, action, cards = re.findall('(\w*) (\w*) (.*)', i)[0]
                cards = cards.replace(' ', '').split(',')
                dct[player] = (action, cards)
            return dct
        else:
            return False

    def winner(self):
        winner = re.findall(self._re_winner, self.hand)[0]
        return {'player': winner[0], 'cash': float(winner[1])}


class Writer:

    def __init__(self):
        pass

    @classmethod
    def header(cls):
        pass

    def hole_cards(self):
        pass

    def preflop(self):
        pass

    def flop(self):
        pass

    def turn(self):
        pass

    def river(self):
        pass

    def showdown(self):
        pass

    def summary(self):
        pass

    def __str__(self):
        s = self.header()
        s += self.hole_cards()
        s += self.preflop()
        s += self.flop()
        s += self.turn()
        s += self.river()
        s += self.showdown()
        s += self.summary()
        return s


class PokerStarsWriter(Writer):

    @classmethod
    def header(cls):
        """
        cls should be Table
        Returns:

        """
        id = f'#{cls.game.game_info.id}'
        stakes = f'(${cls.game.game_info.stakes[0]}/${cls.game.game_info.stakes[1]})'
        time = f' {datetime.date} {datetime.time} {datetime.timezone} '
        table_name = cls.name
        ring_size = '9-max'
        btn = 'Seat #{} is the button'.format(cls.game.btn)
        line1 = f'{id}: Hold\'em No Limit {stakes} {time} '
        line2 = f'Table \'{table_name}\' {ring_size} {btn}'
        s = f'{line1}\n{line2}\n'
        seat_count = 1
        for pos, player in cls.game.players.items():
            if player.isempty():
                seat_count += 1
                continue
            else:
                s += f'Seat {seat_count}: {player.name} (${player.stack} in chips)\n'
                seat_count += 1
        s += f'{cls.game.sb.name} posts small blind ${cls.game.game_info.stakes[0]}\n'
        s += f'{cls.game.bb.name} posts big blind ${cls.game.game_info.stakes[1]}\n'
        return s

    # @classmethod
    # def hole_cards(cls):
    #     return [str(i) for i in cls.game.]

    @classmethod
    def preflop(cls):
        s = '*** HOLE CARDS ***\n'

    @classmethod
    def flop(cls):
        pass

    @classmethod
    def turn(cls):
        pass

    @classmethod
    def river(cls):
        pass

    @classmethod
    def showdown(cls):
        pass

    @classmethod
    def summary(cls):
        pass


class Reader:
    pass


class PokerStarsReader(Writer):
    pass
