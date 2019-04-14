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

from twiggy import quick_setup as QUICK_SETUP
from twiggy import log as LOG

QUICK_SETUP()

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


## todo build a server and host the game, enabling human players to join
## todo build a small gui for playing the game
## todo Work out how to make a intellegant player.


class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.do_checks()

    def __str__(self):
        if isinstance(self.rank, str):
            return "{}{}".format(self.rank, self.suit)
        else:
            return "{}{}".format(self.rank, self.suit)

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

        if self.status not in self.valid_status:
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
        if self.stack - amount < 0:
            logging.info(f'Not enough money to raise by '
                         f'{amount}. Going all in.')
            amount = self.stack
        self.stack -= amount
        return {
            'name': self.name,
            'position': self.position,
            'action': 'raise',
            'amount': amount,
            'status': 'playing'
        }

    def take_turn(self, available, amount=None, probs=None):
        choice = numpy.random.choice(available, p=probs)
        amount = 0.2
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


class EmptySeat(Player):
    name = 'Empty'
    stack = 0
    status = 'Empty'

    def __init__(self, position):
        self.position = position
        super().__init__(name=self.name, stack=self.stack, position=self.position, status=self.status)


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


class Table:
    """
    #todo build a way of saving and loading a players information - stack, stats etc.

    """

    def __init__(self, players, game=None, stakes=(0.05, 0.10), name='tumbleweed', **kwargs):
        self.name = name
        self.players = players
        self.stakes = stakes
        self.game = game
        self.kwargs = kwargs

        if self.game is None:
            self.game = self.create_game()

        self.deck = Deck()
        self.deck.shuffle()

        for i in self.players:
            if not isinstance(self.players[i], Player):
                if isinstance(self.players[i], dict):
                    self.players[i] = Player(**self.players[i])

        if not isinstance(self.players, Players):
            self.players = Players(self.players)

        if len(players) == 2:
            raise ValueError('2 Player Heads-up poker is not yet supported')

    def create_game(self):
        return Game(self.players, **self.kwargs)

    def reset_game(self):
        if self.game is None:
            raise ValueError
        defaults = Game.game_info_defaults()
        defaults.game_id += 1
        self.game.game_info.update(defaults)

        self.deck = Deck().shuffle()
        for pos, pl in self.players.items():
            pl.cards = []

        self.game.players = self._rotate_players()

    def _rotate_players(self):
        new_players = OrderedDict()
        for pos, pl in self.players.items():
            next_pos = str(Position(pos).next_position())
            new_players[next_pos] = pl
            pl.position = next_pos
        self.players = new_players

        for i in ['btn', 'sb', 'bb']:
            if self.players[i].status in ['Empty', 'sitting-out']:
                self.players = self._rotate_players()

        return self.players

    def deal_preflop(self):
        count = 0

        current_pos = 'btn'
        ## deal a maximum of 18 cards. Missing seats are skipped
        while count < 9 * 2:
            current_pos = Position(current_pos).next_position()
            player = self.game.players[str(current_pos)]
            if player.status == 'Empty':
                count += 1
                continue
            card = deepcopy(self.deck.pop())
            player.cards.append(card)
            count += 1

        return self.game

    def deal_flop(self):
        if not isinstance(self.game, Game):
            raise ValueError(f'game argument should be of type "Game" '
                             f'but got "{type(self.game)}" instead.')

        flop = []
        for i in range(3):
            card = self.deck.pop()
            flop.append(card)
        self.game.game_info.community_cards += flop
        assert len(self.game.game_info.community_cards) < 6
        return self.game

    def deal_turn(self):
        if not isinstance(self.game, Game):
            raise ValueError(f'game argument should be of type "Game" '
                             f'but got "{type(self.game)}" instead.')

        self.game.game_info.community_cards += [self.deck.pop()]
        assert len(self.game.game_info.community_cards) < 6
        return self.game

    def deal_river(self):
        if not isinstance(self.game, Game):
            raise ValueError(f'game argument should be of type "Game" '
                             f'but got "{type(self.game)}" instead.')

        self.game.game_info.community_cards += [self.deck.pop()]
        assert len(self.game.game_info.community_cards) < 6
        return self.game

    def next_player(self):
        """
        Update game current position, button, current player
        Args:
            game:

        Returns:

        """
        next_pos = Position()[self.game.game_info.current_position].next_position()
        return self.game.players[next_pos]

    def next_position(self):
        """
        Update game current position, button, current player
        Args:
            game:

        Returns:

        """
        return Position(self.game.game_info.current_position).next_position()

    def next_street(self):
        current_street = self.game.game_info.current_street
        if current_street == 'preflop':
            self.game.game_info.current_street = 'flop'
        elif current_street == 'flop':
            self.game.game_info.current_street = 'turn'
        elif current_street == 'turn':
            self.game.game_info.current_street = 'river'
        else:
            raise ValueError

        return self.game

    def showdown(self):
        if len(self.game.game_info.community_cards) != 5:
            raise ValueError(f'Something has gone wrong. There must be 5 community cards for a showdown. '
                             f'We have "{len(self.game.game_info.community_cards)}"')

        hands = {}
        for pos, player in self.game.players.items():
            if player.status in ['Empty', 'folded', 'sitting-out']:
                continue

            cards = player.cards + self.game.game_info.community_cards
            if len(cards) != 7:
                raise ValueError(f'Total number of cards to evaluate should be 7 but '
                                 f'we got {len(cards)}. That is: {len(self.game.game_info.community_cards)} '
                                 f'community cards and {len(player.cards)} from the player. ')

            hand = Hand(hole_cards=player.cards, community_cards=self.game.game_info.community_cards)
            hands[pos] = hand.eval()

        showdown = self.game.game_info.action_history['showdown']
        for pos, player in self.game.players.items():
            if player.status in ['folded', 'Empty']:
                continue
            showdown.append({
                'name': player.name,
                'hand': hands[pos],
                'winner': True if max(hands) == pos else False
            })

        return self.game

    def play_game(self, to='river'):

        # todo introduce a 'which' argument to only play single street. Mutual exclusive with 'to'. ensure we dont play out of correct order

        # post blinds
        self.take_small_blind()
        self.take_big_blind()

        if to == 'preflop':
            streets = [self.deal_preflop]
        elif to == 'flop':
            streets = [self.deal_preflop, self.deal_flop]
        elif to == 'turn':
            streets = [self.deal_preflop, self.deal_flop,
                       self.deal_turn]
        elif to == 'river':
            streets = [self.deal_preflop, self.deal_flop,
                       self.deal_turn, self.deal_river]
        else:
            raise ValueError

        for street in streets:
            self.game = street()
            ##reset the has_checked flag for current street
            self.game.game_info.check_available = False
            count = 0
            while count != len(self.get_playing()):
                print(count)
                ## get the position of the player who's turn it is
                curr_position = self.game.game_info.current_position
                player = self.game.players[curr_position]
                ## ignore empty, sitting out and folded players
                if player.status in ['Empty', 'sitting-out', 'folded']:
                    self.game.game_info.current_position = self.next_position()
                    continue
                ## get the action from the player
                action = self.request_action(player)
                if action['action'] not in ['check', 'fold']:
                    self.game.game_info.check_available = False
                # update the action history with the players action
                street = self.game.game_info.current_street
                history = self.game.game_info.action_history[street]
                history.append(action)
                ## change to next position
                self.game.game_info.current_position = self.next_position()
                ## add to count
                count += 1
                ## if raise, the other players that are in need to call
                ## so we subtract that number from count
                if action['action'] == 'raise':
                    count = len(self.get_playing())
                    print('new count starting at ,', count)

            if self.game.game_info.current_street != 'river':
                self.game = self.next_street()

        if self.game.game_info.current_street == 'river' and to != 'turn':
            self.game = self.showdown()

            self.game.game_info['winner'] = self.get_winner(self.game)
            # todo make sure winner gets paid
            # winner = self.game.game_info.action_history['showdown']  # ['winner']
            # self.players[winner].stack += self.game.game_info.pot

        return self.game

    def get_playing(self):
        """
        get players that are still playing in this game
        Returns:
            list of players playing in the game
        """
        return {k: v for k, v in self.game.players.items() if v.status == 'playing'}

    def request_action(self, player):
        """
        I think there is a problem with ordering. We need a different or a copy
        of the pot for each round and player so that we can keep track of the evolution of
        the pot in hand history
        Returns:

        """

        ## if the 'has_checked' flag is True, all players before have checked and we also have the option to check
        if self.game.game_info.check_available:
            action = player.take_turn(self.game.action_set_with_check)
        else:
            ## if not, then we remove the option to check
            action = player.take_turn(self.game.action_set_without_check)
        ##
        if action['amount'] is not None:
            self.game.game_info.pot += action['amount']

        ## update player status based on action
        player.status = action['status']

        ## update the action with current pot information for action_history
        action['pot'] = deepcopy(self.game.game_info.pot)
        return action

    @staticmethod
    def get_winner(game):
        if game.game_info.action_history['showdown'] is []:
            raise ValueError('Game has not yet been played to showdown')

        winner = None
        for i in game.game_info.action_history['showdown']:
            if i['winner']:
                winner = i
        return winner

    def play_batch(self, n):
        if not isinstance(n, int):
            raise ValueError(f'n argument must be of type int, not "{type(n)}"')
        winning_hands = []
        for i in range(n):
            LOG.info(f'playing game {i + 1} of {n}')
            g = self.play_game()
            print(g)
            winning_hands.append(g.game_info.winner)
            self.reset_game()
        return winning_hands

    def take_small_blind(self):
        sb = self.players['sb']
        sb.stack -= self.game.game_info.stakes[0]
        self.game.game_info.pot += self.game.game_info.stakes[0]
        sb_action = {
            'name': sb.name,
            'position': 'sb',
            'action': 'small_blind',
            'status': 'playing',
            'amount': self.game.game_info.stakes[0],
            'pot': deepcopy(self.game.game_info.pot)
        }
        self.game.game_info.action_history['preflop'].append(sb_action)

    def take_big_blind(self):
        bb = self.players['bb']
        bb.stack -= self.game.game_info.stakes[1]
        self.game.game_info.pot += self.game.game_info.stakes[1]
        sb_action = {
            'name': bb.name,
            'position': 'bb',
            'action': 'big_blind',
            'status': 'playing',
            'amount': self.game.game_info.stakes[1],
            'pot': deepcopy(self.game.game_info.pot)
        }
        self.game.game_info.action_history['preflop'].append(sb_action)

    def __str__(self):
        return f'Table(name="{self.name}")'


class Game(Bunch):
    action_set_with_check = ['check', 'call', 'raise', 'fold']
    action_set_without_check = ['call', 'raise', 'fold']

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

    @staticmethod
    def game_info_defaults():
        return Bunch({
            'currency': '$',
            'datetime': datetime.now(),
            'game_id': 1,
            'check_available': True,  ## determines which action set a player is presented with
            'betting_equal': False,  ## Criteria for ending a round of betting
            'stakes': [0.10, 0.25],
            'vendor': 'PokerStars',
            'current_street': 'preflop',
            'current_position': 'utg1',
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
        })

    def _set_game_info_defaults(self):
        dct = self.game_info_defaults()
        for k, v in dct.items():
            if k not in self.game_info.keys():
                self.game_info[k] = v

    def summary(self):
        """
        Writes a game summary
        Returns:

        """
        s = ""
        # s += f"PokerStars Hand #{self.game_info.game_id}:  Hold'em No Limit ({self.game_info.currency}" \
        #     f"{self.game_info.stakes[0]}/{self.game_info.currency}{self.game_info.stakes[1]} - {self.game_info.datetime}"
        # s += f"Table '{self.game_info.table_name} 9-max #{self.players['btn'].name} is the button"

    def __str__(self):
        y = Yaml()
        return y.to_yaml_no_player_info(self)

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
        classes = [Game, Position, Players, Player, Card,
                   Bunch, EmptySeat, Hand, HighCard,
                   Pair, TwoPair, ThreeOfAKind,
                   Straight, Flush, FullHouse,
                   StraightFlush, RoyalFlush]
        for i in classes:
            yaml.register_class(i)
        return yaml

    def to_yaml(self, game):
        assert isinstance(game, Game)
        yaml = self._yaml()
        keys_for_yaml = list(game.game_info_defaults().keys()) + [
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

    def to_yaml_no_player_info(self, game):
        assert isinstance(game, Game)
        yaml = self._yaml()
        yaml.default_flow_style = False
        yaml.indent(mapping=2, sequence=2, offset=0)
        dct_for_yaml = {}
        dct_for_yaml['game_info'] = game.game_info
        with StringIO() as buf, redirect_stdout(buf):
            yaml.dump(dct_for_yaml, sys.stdout)
            yaml_string = buf.getvalue()
        assert isinstance(yaml_string, str)
        return yaml_string

    def from_yaml(self, stream):
        yaml = self._yaml()
        return yaml.load(stream)


class Hand:
    def __init__(self, hole_cards, community_cards):
        ## sort in decending order
        self.community_cards = list(reversed(sorted(community_cards)))
        self.hole_cards = list(reversed(sorted(hole_cards)))
        self.cards = self.community_cards + self.hole_cards
        self.cards = list(reversed(sorted(self.cards)))

        ## indicator for whether condition has been met
        self.isa = False

        if len(self.cards) is not 7:
            raise ValueError(f"should be 7 cards but got {len(self.cards)}")

        self.five_best = self.get_five_best()

    def __str__(self):
        return f"{self.__class__.__name__}({self.hole_cards}, {self.community_cards})"

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
            hand_type = hand(self.hole_cards, self.community_cards)
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
        SF = StraightFlush(self.hole_cards, self.community_cards)
        if SF.isa:
            ranks = [i.rank for i in SF.five_best]
            if ranks == ['A', 'K', 'Q', 'J', 10]:
                self.isa = True
                return cards
        else:
            return HighCard(self.hole_cards, self.community_cards)


class StraightFlush(Hand):
    def get_five_best(self):
        S = Straight(self.hole_cards, self.community_cards)
        F = Flush(self.hole_cards, self.community_cards)

        if F.isa and S.isa:
            self.isa = True
            assert F.five_best == S.five_best
            five_best = deepcopy(F.five_best)
            assert len(five_best) == 5
            return five_best
        else:
            return HighCard(self.hole_cards, self.community_cards)


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
            return HighCard(self.hole_cards, self.community_cards)


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
            return HighCard(self.hole_cards, self.community_cards)


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
            return HighCard(self.hole_cards, self.community_cards)


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
            return HighCard(self.hole_cards, self.community_cards)

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
            return HighCard(self.hole_cards, self.community_cards)


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
            return HighCard(self.hole_cards, self.community_cards)


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
            return HighCard(self.hole_cards, self.community_cards).five_best


class HighCard(Hand):
    def get_five_best(self):
        self.isa = True
        return self.cards[:5]


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
