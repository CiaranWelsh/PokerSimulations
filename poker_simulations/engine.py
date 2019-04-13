import os, glob
from collections import OrderedDict, Counter, deque
from random import shuffle
from copy import deepcopy
import logging, numpy
from .bunch import Bunch
from ruamel.yaml import YAML as ryaml
import sys
from io import StringIO
from contextlib import redirect_stdout
from datetime import datetime

FORMAT = "%(name)s: %(levelname)s: %(funcName)s: %(message)s"
logging.basicConfig(format=FORMAT)
LOG = logging.getLogger(__name__)

POSITIONS = {
    0: 'btn',
    1: 'sb',
    2: 'bb',
    3: 'utg1',
    4: 'utg2',
    5: 'mp1',
    6: 'mp2',
    7: 'mp3',
    8: 'co',
}

POSITIONS_INVERTED = {v: k for k, v in POSITIONS.items()}

BETTING_ORDER = ['sb', 'bb', 'utg1', 'utg2',
                 'mp1', 'mp2', 'mp3', 'co',
                 'btn']


class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.do_checks()

    def __str__(self):
        if isinstance(self.rank, str):
            return "Card('{}', '{}')".format(self.rank, self.suit)
        else:
            return "Card({}, '{}')".format(self.rank, self.suit)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        """Overrides the default implementation (unnecessary in Python 3)"""
        x = self.__eq__(other)
        if x is not NotImplemented:
            return not x
        return NotImplemented

    def __hash__(self):
        """Overrides the default implementation"""
        return hash(tuple(sorted(self.__dict__.items())))

    def __lt__(self, other):
        if not isinstance(other, Card):
            raise TypeError('Cannot make comparison between Card and "{}"'.format(type(other)))
        return self.rank_order[self.rank] < self.rank_order[other.rank]

    def __le__(self, other):
        if not isinstance(other, Card):
            raise TypeError('Cannot make comparison between Card and "{}"'.format(type(other)))
        return self.rank_order[self.rank] <= self.rank_order[other.rank]

    def __gt__(self, other):
        if not isinstance(other, Card):
            raise TypeError('Cannot make comparison between Card and "{}"'.format(type(other)))
        return self.rank_order[self.rank] > self.rank_order[other.rank]

    def __ge__(self, other):
        if not isinstance(other, Card):
            raise TypeError('Cannot make comparison between Card and "{}"'.format(type(other)))
        return self.rank_order[self.rank] >= self.rank_order[other.rank]

    def do_checks(self):
        if self.rank not in ['A', 'K', 'Q', 'J'] + list(range(2, 11)):
            raise ValueError('"num" should be between A, K, Q, J or a number from 2 to 10. Got "{}"'.format(self.num))

        if self.suit not in ['H', 'D', 'S', 'C']:
            raise ValueError('"suit" should be one of H, D, S or C. Got "{}"'.format(self.suit))

    @property
    def rank_order(self):
        """
        create a dict for internal representation
        of ranks such that picture cards are correctly ordered
        :return:
        """
        d = OrderedDict()
        order = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K', 'A']
        for i in range(len(order)):
            d[order[i]] = i
        return d

    @property
    def internal_rank(self):
        """
        return the internal rank of current card from rank order
        :return:
        """
        return self.rank_order[self.rank]


class Deck:
    def __init__(self):
        self.cards = self.create()
        self.shuffle()

    def __str__(self):
        return str(self.cards)

    def __len__(self):
        return len(self.cards)

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        """Overrides the default implementation (unnecessary in Python 3)"""
        x = self.__eq__(other)
        if x is not NotImplemented:
            return not x
        return NotImplemented

    def __hash__(self):
        """Overrides the default implementation"""
        return hash(tuple(sorted(self.__dict__.items())))

    def create(self):
        cards = deque()
        for rank in ['A', 'K', 'Q', 'J'] + list(range(2, 11)):
            for suit in ['H', 'C', 'S', 'D']:
                cards.append(Card(rank, suit))
        return cards

    def shuffle(self):
        shuffle(self.cards)
        return self.cards

    def pop(self):
        card = self.cards.pop()
        return deepcopy(card)

    def get(self, rank, suit):
        for i in self.cards:
            if i.rank == rank and i.suit == suit:
                self.cards.remove(i)
                return i


class Stack(numpy.float):

    def __init__(self, amount, currency='$'):
        super().__init__()
        self.amount = amount
        self.currency = currency

    def __str__(self):
        return f"stack({self.currency}{round(self.amount, 2)})"

    def __repr__(self):
        return self.__str__()


class Player:

    def __init__(self, name, stack,
                 position, cards=[],
                 status='playing'):
        self.name = name
        if not isinstance(stack, Stack):
            stack = Stack(stack)

        self.stack = stack
        self.position = position
        self.status = status
        self.cards = deepcopy(cards)
        self.hole_cards_hidden = True

        if self.status not in ['playing', 'not-playing']:
            raise ValueError

    def __str__(self):
        return f"Player(name=\"{self.name}\", stack={self.stack}, position=\"{self.position}\", status=\"{self.status}\")"

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
        return {'name': self.name, 'action': 'check', 'amount': None, 'status': 'playing'}

    def fold(self):
        return {'name': self.name, 'action': 'fold', 'amount': None, 'status': 'folded'}

    def call(self, amount):
        if self.stack - amount < 0:
            LOG.info('Not enough money to call. Going all in.')
            amount = self.stack
        self.stack -= amount
        return {'name': self.name, 'action': 'call', 'amount': amount, 'status': 'playing'}

    def raise_(self, amount):
        if self.stack - amount < 0:
            LOG.info(f'Not enough money to raise by '
                     f'{amount}. Going all in.')
            amount = self.stack
        self.stack -= amount
        return {'name': self.name, 'action': 'raise', 'amount': amount, 'status': 'playing'}

    def take_turn(self, available, amount=None, probs=None):
        choice = numpy.random.choice(available, p=probs)
        amount = 10
        assert choice in ['check', 'call', 'raise', 'fold', 'raise_']
        if choice == 'check':
            return self.check()
        elif choice == 'call':
            return self.call(amount)
        elif choice == 'raise':
            return self.raise_(amount)
        elif choice == 'fold':
            return self.fold()
        else:
            raise ValueError


class Players:

    def __init__(self, iterable):
        self.num_players = len(iterable)

        if isinstance(iterable, list):
            iterable = {position: player for position, player in zip(
                list(POSITIONS.values())[:self.num_players], iterable)}

        for k in iterable:
            if k not in POSITIONS.values():
                raise ValueError(f'"{k}" is not a valid key for "Players".'
                                 f' These are valid: {POSITIONS.values()}')

        self.iterable = iterable

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

    def items(self):
        return self.iterable.items()

    def __len__(self):
        return len(self.iterable)

    def __iter__(self):
        return self.iterable.__iter__()

    def __next__(self):
        return self.iterable.__next__()

    @staticmethod
    def get_default_players():
        seats = numpy.linspace(1, 9, num=9)
        positions = numpy.linspace(1, 9, num=9)

        shuffle(seats)
        shuffle(positions)
        p = [Player(name='player{}'.format(i), stack=1.0,
                    seat=seats[i], position=POSITIONS[positions[i]]) for i in range(1, 9)]
        return p


class Dealer:

    def __init__(self):
        self.deck = Deck()
        self.deck.shuffle()

    def deal_preflop(self, game):
        count = 0

        current_pos = Btn()
        while count < len(game.players) * 2:
            current_pos = current_pos.next_position()
            try:
                player = game.players[str(current_pos)]
            except KeyError:
                continue
            card = deepcopy(self.deck.pop())
            player.cards.append(card)
            count += 1

        return game

    def deal_flop(self, game):
        if not isinstance(game, Game):
            raise ValueError(f'game argument should be of type "Game" '
                             f'but got "{type(game)}" instead.')

        flop = []
        for i in range(3):
            card = self.deck.pop()
            flop.append(card)
        game.game_info.community_cards += flop
        assert len(game.game_info.community_cards) < 6
        return game

    def deal_turn(self, game):
        if not isinstance(game, Game):
            raise ValueError(f'game argument should be of type "Game" '
                             f'but got "{type(game)}" instead.')

        game.game_info.community_cards += [self.deck.pop()]
        assert len(game.game_info.community_cards) < 6
        return game

    def deal_river(self, game):
        if not isinstance(game, Game):
            raise ValueError(f'game argument should be of type "Game" '
                             f'but got "{type(game)}" instead.')

        game.game_info.community_cards += [self.deck.pop()]
        assert len(game.game_info.community_cards) < 6
        return game

    def next_player(self, game):
        """
        Update game current position, button, current player
        Args:
            game:

        Returns:

        """
        next_pos = Position()[game.game_info.current_position].next_position()
        return game.players[next_pos]

    def next_position(self, game):
        """
        Update game current position, button, current player
        Args:
            game:

        Returns:

        """
        return Position()[game.game_info.current_position].next_position()

    def next_street(self, game):
        current_street = game.game_info.current_street
        if current_street == 'preflop':
            game.game_info.current_street = 'flop'
        elif current_street == 'flop':
            game.game_info.current_street = 'turn'
        elif current_street == 'turn':
            game.game_info.current_street = 'river'
        else:
            game.game_info.current_street = 'summary'

        return game

    def request_action(self, game):
        curr_position = game.game_info.current_position
        player = game.players[curr_position]
        if player.status == 'sitting-out':
            return game
        if game.game_info.has_checked:
            actions = player.take_turn(game.action_set2)
        else:
            actions = player.take_turn(game.action_set1)
        street = game.game_info.current_street
        game.game_info.action_history[street].append(actions)
        return game

    def showdown(self, game):
        if len(game.game_info.community_cards) != 5:
            raise ValueError(f'Something has gone wrong. There must be 5 community cards for a showdown. '
                             f'We have "{len(game.game_info.community_cards)}"')

        hands = {}
        for player in game.players:
            if game.players[player].status == 'folded':
                continue
            hand = Hand(game.players[player].cards + game.game_info.community_cards)
            hands[player] = hand.eval()
        winning_pos = max(hands)
        winning_player = game.players[winning_pos]
        winning_hand = hands[winning_pos]
        game.game_info.hand_evals = hand
        game.game_info.winner = {
            'winning_player': winning_player,
            'winning_hand': winning_hand,
        }
        return game

        # for k, v in dct.items():
        #     print(k, v)
        # print(game.game_info.community_cards)


class Position:
    positions = ['btn', 'sb', 'bb',
                 'utg1', 'utg2', 'mp1',
                 'mp2', 'mp3', 'co']

    def __init__(self, position='btn'):
        self.position = position

    def next_position(self):
        pass

    def __str__(self):
        return self.position

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, item):
        if isinstance(item, Position):
            item = str(item)
        if item not in self.positions:
            raise ValueError(f'item must be one of {self.positions}. Got "{item}" ')
        if item == 'btn':
            return Btn()
        elif item == 'sb':
            return Sb()
        elif item == 'bb':
            return Bb()
        elif item == 'utg1':
            return Utg1()
        elif item == 'utg2':
            return Utg2()
        elif item == 'mp1':
            return Mp1()
        elif item == 'mp2':
            return Mp2()
        elif item == 'mp3':
            return Mp3()
        elif item == 'co':
            return Co()

    def get_position(self):
        if self.position == 'btn':
            return Btn()
        elif self.position == 'sb':
            return Sb()
        elif self.position == 'bb':
            return Bb()
        elif self.position == 'utg1':
            return Utg1()
        elif self.position == 'utg2':
            return Utg2()
        elif self.position == 'mp1':
            return Mp1()
        elif self.position == 'mp2':
            return Mp2()
        elif self.position == 'mp3':
            return Mp3()
        elif self.position == 'co':
            return Co()


class Btn(Position):

    def __init__(self):
        self.position = 'btn'
        super().__init__(self.position)

    def next_position(self):
        return Sb()


class Sb(Position):

    def __init__(self):
        self.position = 'sb'
        super().__init__(self.position)

    def next_position(self):
        return Bb()


class Bb(Position):

    def __init__(self):
        self.position = 'bb'
        super().__init__(self.position)

    def next_position(self):
        return Utg1()


class Utg1(Position):

    def __init__(self):
        self.position = 'utg1'
        super().__init__(self.position)

    def next_position(self):
        return Utg2()


class Utg2(Position):

    def __init__(self):
        self.position = 'utg2'
        super().__init__(self.position)

    def next_position(self):
        return Mp1()


class Mp1(Position):

    def __init__(self):
        self.position = 'mp1'
        super().__init__(self.position)

    def next_position(self):
        return Mp2()


class Mp2(Position):

    def __init__(self):
        self.position = 'mp2'
        super().__init__(self.position)

    def next_position(self):
        return Mp3()


class Mp3(Position):

    def __init__(self):
        self.position = 'mp3'
        super().__init__(self.position)

    def next_position(self):
        return Co()


class Co(Position):

    def __init__(self):
        self.position = 'co'
        super().__init__(self.position)

    def next_position(self):
        return Btn()


class Table:

    def __init__(self, players, stakes=(0.05, 0.10), name='tumbleweed'):
        self.name = name
        self.players = players
        self.stakes = stakes
        self.dealer = Dealer()

        for i in self.players:
            if not isinstance(self.players[i], Player):
                self.players[i] = Player(**self.players[i])

        if not isinstance(self.players, Players):
            self.players = Players(self.players)

        ## initialise seats
        # self.seats = self._create_seats()
        # self.seats = self._fill_seats()

    def play_game(self, game=None, to='river'):

        if to == 'preflop':
            streets = [self.dealer.deal_preflop]
        elif to == 'flop':
            streets = [self.dealer.deal_preflop, self.dealer.deal_flop]
        elif to == 'turn':
            streets = [self.dealer.deal_preflop, self.dealer.deal_flop,
                       self.dealer.deal_turn]
        elif to == 'river':
            streets = [self.dealer.deal_preflop, self.dealer.deal_flop,
                       self.dealer.deal_turn, self.dealer.deal_river]
        else:
            raise ValueError

        if game is None:
            game = Game(self.players)

        for street in streets:
            game = street(game)
            game = self.street_action(game)

        if game.game_info.current_street == 'river':
            game = self.dealer.showdown(game)

            game.players[game.info.winner['winning_player'].position].stack += game.game_info.pot
        if game.game_info.current_street != 'river':
            game = self.next_street(game)
        return game

    def next_street(self, game):
        return self.dealer.next_street(game)

    def street_action(self, game):
        count = 0
        while count != len(game.players):
            game = self.dealer.request_action(game)
            next_pos = self.dealer.next_position(game)
            game.game_info.current_position = next_pos
            count += 1
        return game

    def __str__(self):
        return f'Table(name="{self.name}")'

    def restart(self):
        pass
        # print(self.seats)


class Game(Bunch):
    action_set1 = ['check', 'call', 'raise', 'fold']
    action_set2 = ['call', 'raise', 'fold']

    def __init__(self, players, game_info={}):
        self.game_info = Bunch(game_info)
        self.players = players

        if isinstance(self.players, dict):
            self.players = Players(self.players)

        if isinstance(self.players, list):
            raise TypeError('list objects are not accepted. '
                            'Please seat your players in a dict '
                            'or Players object. ')

        # if not isinstance(self.players, Players):
        #     raise ValueError(f'Expected a "Players" object but got "{type(self.players)}" ')

        self._btn = [v.name for k, v in self.players.items() if k == 'btn'][0]
        self._sb = [v.name for k, v in self.players.items() if k == 'sb'][0]
        self._bb = [v.name for k, v in self.players.items() if k == 'bb'][0]

        self.pot = 0
        self.seats = self._create_seats()
        self._validate_players()
        self.seats = self._fill_seats()
        self._set_game_info_defaults()

    def _game_info_defaults(self):
        return Bunch({
            'currency': '$',
            'datetime': datetime.now(),
            'game_id': None,
            'has_checked': False,
            'num_players': len(self.players),
            'stakes': [0.10, 0.25],
            'vendor': 'PokerStars',
            'current_street': 'preflop',
            'current_position': Position()['utg1'],
            'community_cards': [],
            'pot': 0,
            'call_amount': None,
            'action_history': dict(
                preflop=[],
                flop=[],
                turn=[],
                river=[],
                showdown=[],
            ),
            'hands_evals': None,
            'winner': None
        })

    def summary(self):
        """
        Writes a game summary
        Returns:

        """
        s = ""
        # s += f"PokerStars Hand #{self.game_info.game_id}:  Hold'em No Limit ({self.game_info.currency}" \
        #     f"{self.game_info.stakes[0]}/{self.game_info.currency}{self.game_info.stakes[1]} - {self.game_info.datetime}"
        # s += f"Table '{self.game_info.table_name} 9-max #{self.players['btn'].name} is the button"

    def _set_game_info_defaults(self):
        dct = self._game_info_defaults()
        for k, v in dct.items():
            if k not in self.game_info.keys():
                self.game_info[k] = v

    def __str__(self):
        return self.to_yaml()

    def _validate_players(self):
        if isinstance(self.players, list):
            self.players = Players(self.players)

        if not isinstance(self.players, Players):
            raise TypeError(f'Expected a list of dict for "players" argument. Got "{type(self.players)}"')

        if len(self.players) == 2:
            assert self.btn != []
            assert self.sb != []
        else:
            assert self.btn != []
            assert self.sb != []
            assert self.bb != []

    @property
    def btn(self):
        return self._btn

    @btn.setter
    def btn(self, new):
        if not isinstance(new, Player):
            raise TypeError(f'Expected instance of type "Player" but '
                            f'got "{type(new)}"')
        self._btn = new

    @property
    def sb(self):
        return self._sb

    @sb.setter
    def sb(self, new):
        if not isinstance(new, Player):
            raise TypeError(f'Expected instance of type "Player" but '
                            f'got "{type(new)}"')
        self._sb = new

    @property
    def bb(self):
        return self._bb

    @bb.setter
    def bb(self, new):
        if not isinstance(new, Player):
            raise TypeError(f'Expected instance of type "Player" but '
                            f'got "{type(new)}"')
        self._bb = new

    def _fill_seats(self):
        for i in range(len(self.players)):
            self.seats[i] = self.players[i]

        return self.seats

    def _create_seats(self):
        """
        create a empty slot for each potential player
        Returns:
            dict
        """
        return {i: 'empty' for i in range(9)}

    def to_yaml(self):
        y = Yaml()
        return y.to_yaml(self)


class Yaml:

    def __init__(self):
        pass

    def _yaml(self):
        yaml = ryaml()
        classes = [Game, Position, Utg1, Stack,
                   Btn, Utg2, Mp1, Mp2, Mp3,
                   Co, Sb, Bb, Players, Player, Card,
                   Bunch]
        for i in classes:
            yaml.register_class(i)
        return yaml

    def to_yaml(self, game):
        assert isinstance(game, Game)
        yaml = self._yaml()
        keys_for_yaml = list(game._game_info_defaults().keys()) + [
            'players'
        ]
        # dct_for_yaml = {k: v for k, v in game.game_info.items() if k in keys_for_yaml}
        # dct_for_yaml.update({k: v for k, v in game.__dict__.items() if k in keys_for_yaml})
        yaml.default_flow_style = False
        yaml.indent(mapping=2, sequence=2, offset=0)
        dct_for_yaml = {}
        dct_for_yaml['game_info'] = game.game_info
        dct_for_yaml['players'] = game.players
        with StringIO() as buf, redirect_stdout(buf):
            yaml.dump(dct_for_yaml, sys.stdout)
            yaml_string = buf.getvalue()
        assert isinstance(yaml_string, str)
        return yaml_string

    def from_yaml(self, stream):
        yaml = self._yaml()
        return yaml.load(stream)


class ActionHistory:
    streets = ['preflop', 'flop', 'turn', 'river', 'showdown']

    def __init__(self):
        self.history = {
            'preflop': [],
            'flop': [],
            'turn': [],
            'river': [],
            'showdown': [],
        }

    def add(self, history, which='preflop'):
        assert which in self.streets
        self.history[which].append(history)


class Hand:
    def __init__(self, cards):
        ## sort in decending order
        self.cards = list(reversed(sorted(cards)))

        ## indicator for whether condition has been met
        self.isa = False

        if len(cards) is not 7:
            raise ValueError("should be 7 cards")

        self.five_best = self.get_five_best()

    def __str__(self):
        return str("{}({})".format(self.__class__.__name__, self.cards))

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        """Overrides the default implementation (unnecessary in Python 3)"""
        x = self.__eq__(other)
        if x is not NotImplemented:
            return not x
        return NotImplemented

    def __hash__(self):
        """Overrides the default implementation"""
        return hash(tuple(sorted(self.__dict__.items())))

    def __lt__(self, other):
        if not isinstance(other, Hand):
            raise TypeError('Cannot make comparison between Hand and "{}"'.format(type(other)))
        if self.internal_rank == other.internal_rank:
            self_sum = sum([i.internal_rank for i in self.five_best])
            other_sum = sum([i.internal_rank for i in other.five_best])
            return self_sum < other_sum

        ## otherwise compare the internal ranks
        else:
            return self.internal_rank < other.internal_rank

    def __le__(self, other):
        if not isinstance(other, Hand):
            raise TypeError('Cannot make comparison between Hand and "{}"'.format(type(other)))
        if self.internal_rank == other.internal_rank:
            self_sum = sum([i.internal_rank for i in self.five_best])
            other_sum = sum([i.internal_rank for i in other.five_best])
            return self_sum <= other_sum

        ## otherwise compare the internal ranks
        else:
            return self.internal_rank <= other.internal_rank

    def __gt__(self, other):
        if not isinstance(other, Hand):
            raise TypeError('Cannot make comparison between Hand and "{}"'.format(type(other)))

        if self.internal_rank == other.internal_rank:
            self_sum = sum([i.internal_rank for i in self.five_best])
            other_sum = sum([i.internal_rank for i in other.five_best])
            return self_sum > other_sum

        ## otherwise compare the internal ranks
        else:
            return self.internal_rank > other.internal_rank

    def __ge__(self, other):
        if not isinstance(other, Hand):
            raise TypeError('Cannot make comparison between Hand and "{}"'.format(type(other)))

        if self.internal_rank == other.internal_rank:
            self_sum = sum([i.internal_rank for i in self.five_best])
            other_sum = sum([i.internal_rank for i in other.five_best])
            return self_sum <= other_sum

        ## otherwise compare the internal ranks
        else:
            return self.internal_rank <= other.internal_rank

    @staticmethod
    def hand_rank_order():
        d = OrderedDict()
        hand_order = [
            'HighCard',
            'Pair',
            'TwoPair',
            'ThreeOfAKind',
            'Straight',
            'Flush',
            'FullHouse',
            'FourOfAKind',
            'StraightFlush',
            'RoyalFlush'
        ]
        for i in range(len(hand_order)):
            d[hand_order[i]] = i

        return d

    @property
    def internal_rank(self):
        return self.hand_rank_order()[self.__class__.__name__]

    def get_five_best(self):
        """
        Get five best cards. Method is designed to be
        overriden in subclasses.
        :return:
        """
        pass

    def eval(self):
        """
        return the maximum hand
        :return:
        """
        isa_list = []
        for hand in Hand.__subclasses__():
            hand_type = hand(self.cards)
            if hand_type.isa:
                isa_list.append(hand_type)

        max_isalist = max(isa_list)

        return max_isalist

    def max(self, lst):
        if not isinstance(lst, list):
            raise TypeError('lst argument should be list')
        max = lst[0]
        for i in lst:
            if i > max:
                max = i
        return max


class RoyalFlush(Hand):
    def get_five_best(self):
        cards = deepcopy(self.cards)
        SF = StraightFlush(cards)
        if SF.isa:
            ranks = [i.rank for i in SF.five_best]
            if ranks == ['A', 'K', 'Q', 'J', 10]:
                self.isa = True
                return cards
        else:
            return HighCard(cards)


class StraightFlush(Hand):
    def get_five_best(self):
        cards = deepcopy(self.cards)
        S = Straight(cards)
        F = Flush(cards)

        if F.isa and S.isa:
            self.isa = True
            assert F.five_best == S.five_best
            five_best = deepcopy(F.five_best)
            assert len(five_best) == 5
            return five_best
        else:
            return HighCard(cards)


class FourOfAKind(Hand):
    def get_five_best(self):
        cards = deepcopy(self.cards)

        ## get most common card
        most_common = Counter([i.rank for i in cards]).most_common(1)

        if most_common[0][1] is 4:
            self.isa = True
            five_best = []
            for i in most_common:
                rank = i[0]
                for card in cards:
                    if card.rank is rank:
                        five_best.append(card)
            remaining = list(set(five_best).symmetric_difference(set(cards)))
            ## sort remaining
            remaining = list(reversed(sorted(remaining)))
            five_best += [remaining[0]]

            assert len(five_best) is 5

            return five_best
        else:
            return HighCard(cards)


class FullHouse(Hand):
    def get_five_best(self):
        cards = deepcopy(self.cards)
        ## get most common card
        most_common = Counter([i.rank for i in cards]).most_common(2)

        if most_common[0][1] is 3 and most_common[1][1] is 2:
            self.isa = True
            five_best = []
            for i in most_common:
                rank = i[0]
                for card in cards:
                    if card.rank is rank:
                        five_best.append(card)

            assert len(five_best) is 5

            return list(reversed(sorted(five_best)))
        else:
            return HighCard(cards)


class Flush(Hand):
    def get_five_best(self):
        cards = deepcopy(self.cards)
        cards = list(reversed(sorted(cards)))
        most_common = Counter([i.suit for i in cards]).most_common(1)
        most_common_count = most_common[0][1]
        most_common_suit = most_common[0][0]
        five_best = []
        if most_common_count >= 5:
            self.isa = True
            for card in cards:
                if card.suit == most_common_suit:
                    five_best.append(card)

            five_best = five_best[:5]
            assert len(five_best) is 5

            return list(reversed(sorted(five_best)))

        else:
            return HighCard(self.cards)


class Straight(Hand):
    def get_five_best(self):
        cards = sorted(deepcopy(self.cards))
        internal_ranks = [i.internal_rank for i in cards]
        possible_straights = OrderedDict()
        for i in range(9):
            possible_straights[i] = list(range(i, i + 5))
        possible_straights[12] = [12, 0, 1, 2, 3]

        best_five = []
        for k, v in list(possible_straights.items()):
            if set(v).issubset(set(internal_ranks)):
                for card in cards:
                    for i in v:
                        if card.internal_rank is i:
                            best_five.append(card)

        if best_five == []:
            return HighCard(cards)

        else:
            self.isa = True
            best_five = set(best_five)
            best_five = list(reversed(sorted(best_five)))
            best_five = best_five[:5]
            assert len(best_five) == 5
            return list(reversed(sorted(best_five)))


class ThreeOfAKind(Hand):
    def get_five_best(self):
        cards = deepcopy(self.cards)

        ## get most common card
        most_common = Counter([i.rank for i in cards]).most_common(1)

        if most_common[0][1] is 3:
            self.isa = True
            five_best = []
            for i in most_common:
                rank = i[0]
                for card in cards:
                    if card.rank is rank:
                        five_best.append(card)
            remaining = list(set(five_best).symmetric_difference(set(cards)))
            ## sort remaining
            remaining = list(reversed(sorted(remaining)))
            five_best += remaining[:2]

            assert len(five_best) is 5

            return five_best
        else:
            return HighCard(cards)


class TwoPair(Hand):
    def get_five_best(self):
        cards = deepcopy(self.cards)

        ## get most common card
        most_common = Counter([i.rank for i in cards]).most_common(2)

        if most_common[0][1] is 2 and most_common[1][1] is 2:
            self.isa = True
            five_best = []
            for i in most_common:
                rank = i[0]
                for card in cards:
                    if card.rank is rank:
                        five_best.append(card)
            remaining = list(set(five_best).symmetric_difference(set(cards)))
            ## sort remaining
            remaining = list(reversed(sorted(remaining)))
            five_best.append(remaining[0])

            assert len(five_best) is 5

            return five_best
        else:
            return HighCard(cards)


class Pair(Hand):
    def get_five_best(self):
        ## make copy so we don't loose original
        cards = deque(deepcopy(self.cards))

        ## get most common card
        most_common = Counter([i.rank for i in cards]).most_common(1)
        most_common_rank = most_common[0][0]
        most_common_count = most_common[0][1]

        five_best = []

        if most_common_count is 2:
            self.isa = True
            for i in range(len(cards)):
                if cards[i].rank is most_common_rank:
                    ## add the pair to 5 best
                    five_best.append(cards[i])

            ## remove the two cards from cards
            remaining = list(set(five_best).symmetric_difference(set(cards)))
            remaining = list(reversed(sorted(remaining)))

            ## since superclass already sorts the cards
            ## we now just take the top 3 to complete the 5 best
            five_best += remaining[:3]

            assert len(five_best) is 5

            return five_best

        else:
            return HighCard(cards).five_best


class HighCard(Hand):
    def get_five_best(self):
        self.isa = True
        return self.cards[:5]
