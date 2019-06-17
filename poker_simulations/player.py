import logging
from copy import deepcopy

from .constants import POSITIONS, POSITIONS_INVERTED


class Player:
    """
    How can I make a player intelligent?

    #todo Give player stats


    """
    valid_status = ['playing', 'not-playing', 'folded', 'Empty']

    def __init__(self, name, stack,
                 position, cards=[],
                 status='playing'):
        self.name = name
        self.stack = stack
        self.position = position
        self.status = status
        self.cards = deepcopy(cards)
        self.hole_cards_hidden = True
        # self.mind_control = mind_control
        # self.hypnotized = False
        # if self.mind_control is not []:
        #     self.hypnotized = True

        if self.status not in self.valid_status:
            raise ValueError

    def __str__(self):
        return f"{self.__class__.__name__}(name=\"{self.name}\", stack={self.stack}, position=\"{self.position}\", status=\"{self.status}\")"

    def __repr__(self):
        return self.__str__()

    def bet(self, amount):
        self.stack -= amount
        return amount

    def stats(self):
        """
        Will eventually have a bunch of stats that I'll be able
        to call up on the players.
        Returns:

        """

    def give_card(self, card):
        if len(self.cards) > 2:
            raise ValueError(f'A person can hold a maximum of two cards. '
                             f'Player "{self.name}" has "{len(self.cards)}" '
                             f'({self.cards})')
        self.cards.append(card)

    def remove_cards(self):
        self.cards = []

    def __gt__(self, other):
        if not isinstance(other, Player):
            raise TypeError('Cannot make comparison between Player and "{}"'.format(type(other)))

        return POSITIONS_INVERTED[self.position] > POSITIONS_INVERTED[other.position]

    def __lt__(self, other):
        if not isinstance(other, Player):
            raise TypeError('Cannot make comparison between Player and "{}"'.format(type(other)))

        return POSITIONS_INVERTED[self.position] < POSITIONS_INVERTED[other.position]

    def __ge__(self, other):
        if not isinstance(other, Player):
            raise TypeError('Cannot make comparison between Player and "{}"'.format(type(other)))
        return POSITIONS_INVERTED[self.position] >= POSITIONS_INVERTED[other.position]

    def __le__(self, other):
        if not isinstance(other, Player):
            raise TypeError('Cannot make comparison between Player and "{}"'.format(type(other)))
        return POSITIONS_INVERTED[self.position] <= POSITIONS_INVERTED[other.position]

    def __eq__(self, other):
        if not isinstance(other, Player):
            raise TypeError('Cannot make comparison between Player and "{}"'.format(type(other)))
        return POSITIONS_INVERTED[self.position] == POSITIONS_INVERTED[other.position]

    def __ne__(self, other):
        if not isinstance(other, Player):
            raise TypeError('Cannot make comparison between Player and "{}"'.format(type(other)))
        return POSITIONS_INVERTED[self.position] != POSITIONS_INVERTED[other.position]

    def check(self):
        return {
            'name': self.name,
            'action': 'check',
            'position': self.position,
            'amount': None,
            'status': 'playing'
        }

    def fold(self):
        return {
            'name': self.name,
            'position': self.position,
            'action': 'fold',
            'amount': None,
            'status': 'folded'}

    def call(self, amount):
        if amount is None:
            raise ValueError('Cannot call "None"')
        if self.stack - amount < 0:
            logging.info('Not enough money to call. Going all in.')
            amount = self.stack
        self.stack -= amount
        return {
            'name': self.name,
            'position': self.position,
            'action': 'call',
            'amount': amount,
            'status': 'playing'
        }

    def raise_(self, amount):
        action = 'raise'
        if amount >= self.stack:
            logging.info(f'Not enough money to raise by '
                         f'{amount}. Going all in.')
            amount = self.stack
            action = 'all-in'
        self.stack -= amount
        return {
            'name': self.name,
            'position': self.position,
            'action': action,
            'amount': amount,
            'status': 'playing'
        }

    def take_turn(self, available, betting_dct, bb):
        return {
            'player': self.name,
            'action': 'call',
            'amount': bb
        }

    def process_turn(self, available, betting_dct, bb):
        if not isinstance(bb, float):
            raise ValueError('bb arg should be of type float not "{}"'.format(type(bb)))
        turn_info = self.take_turn(available, betting_dct, bb)
        if not isinstance(turn_info, dict):
            raise ValueError('An implementation of "take_turn" must return '
                             'a dict')
        choice = turn_info['action']
        assert choice in ['check', 'call', 'raise', 'fold', 'all-in',
                          'raises', 'calls', 'checks', 'folds', 'bets',
                          'bet'], choice
        if choice in ['checks', 'calls', 'raises',
                      'folds', 'bets']:
            choice = choice[:-1]
        amount_to_call = max(betting_dct.values()) - betting_dct[self.position]
        amount_to_raise = max(betting_dct.values()) + bb * 1

        if amount_to_call == 0 and choice == 'call':
            choice == 'check'

        if amount_to_call >= self.stack or amount_to_raise >= self.stack:
            choice = 'all-in'

        if choice == 'check':
            return self.check()
        elif choice in ['call', 'bet']:
            return self.call(amount_to_call)
        elif choice == 'raise':
            return self.raise_(amount_to_raise)
        elif choice == 'all-in':
            return self.raise_(self.stack)
        elif choice == 'fold':
            return self.fold()
        else:
            raise ValueError('choice "{}" is not a valid choice'.format(choice))

    def isempty(self):
        if self.status == 'Empty':
            return True

        else:
            return False


class EmptySeat(Player):
    name = 'Empty'
    stack = 0
    status = 'Empty'

    def __init__(self, position):
        self.position = position
        super().__init__(name=self.name, stack=self.stack, position=self.position, status=self.status)


class Slave(Player):

    def __init__(self, name, stack,
                 position, line, cards=[],
                 status='playing', ):
        super().__init__(name, stack, position,
                         cards=cards, status=status)
        self.stack = stack
        self.position = position
        self.line = line
        self.cards = cards
        self.status = status

    def take_turn(self, *args, **kwargs):
        # print('line', self.line)
        # turn = self.line[self.name]
        # if turn == []:
        #     return {}
        # else:
        return self.line.pop(0)
        # for action in self.line:
        #     if action not in ['preflop', 'flop', 'turn', 'river', 'showdown']:
        #         yield action


class Players:

    def __init__(self, iterable={}):
        self.num_players = len(iterable)

        if isinstance(iterable, list):
            iterable = {position: player for position, player in zip(
                list(POSITIONS.values())[:self.num_players], iterable)}

        for k in iterable:
            if k not in POSITIONS.values():
                raise ValueError(f'"{k}" is not a valid key for "Players".'
                                 f' These are valid: {POSITIONS.values()}')

        self.iterable = iterable

        for pos in POSITIONS:
            if POSITIONS[pos] not in self.iterable:
                self.iterable[POSITIONS[pos]] = EmptySeat(POSITIONS[pos])

    def __str__(self):
        return self.iterable.__str__()

    def __repr__(self):
        return self.iterable.__repr__()

    def __getitem__(self, item):
        if isinstance(item, int):
            item = POSITIONS[item]
        if isinstance(item, Position):
            item = str(item)
        assert isinstance(item, str)
        return self.iterable[item]

    def __delitem__(self, key):
        assert key in self.iterable
        del self.iterable[key]

    def __setitem__(self, key, value):
        if key not in POSITIONS.values():
            raise ValueError(f'Key for Players class must be one of "{POSITIONS.values()}"')
        self.iterable[key] = value

    def items(self):
        return self.iterable.items()

    def __len__(self):
        return len(self.iterable)

    def __iter__(self):
        return self.iterable.__iter__()

    def __next__(self):
        return self.iterable.__next__()

    @staticmethod
    def full_ring(base_name='player', stack=25, status='playing'):
        p = {}
        for i, pos in POSITIONS.items():
            p[pos] = Player(name='{}{}'.format(base_name, i),
                            stack=stack, status=status, position=pos)
        return p


class Position:
    positions = ['btn', 'sb', 'bb',
                 'utg1', 'utg2', 'mp1',
                 'mp2', 'mp3', 'co']

    def __init__(self, position='btn'):
        self.position = position

    def next_position(self):
        if self.position == 'btn':
            return 'sb'
        elif self.position == 'sb':
            return 'bb'
        elif self.position == 'bb':
            return 'utg1'
        elif self.position == 'utg1':
            return 'utg2'
        elif self.position == 'utg2':
            return 'mp1'
        elif self.position == 'mp1':
            return 'mp2'
        elif self.position == 'mp2':
            return 'mp3'
        elif self.position == 'mp3':
            return 'co'
        elif self.position == 'co':
            return 'btn'

    def __str__(self):
        return self.position

    def __repr__(self):
        return self.__str__()

    # def get_position(self):