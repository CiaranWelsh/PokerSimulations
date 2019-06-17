from collections import OrderedDict, deque
from random import shuffle
from copy import deepcopy
import numpy as np

from poker_simulations.eval import Hand, RoyalFlush, StraightFlush, FullHouse, Flush, Straight, ThreeOfAKind, TwoPair, \
    Pair, HighCard
from poker_simulations.player import Player, EmptySeat, Slave, Players, Position
from ruamel.yaml import YAML as ryaml
import sys
from io import StringIO
from contextlib import redirect_stdout
from datetime import datetime

from twiggy import quick_setup as QUICK_SETUP
from twiggy import log as LOG
from .io import PokerStarsParser, PokerStarsWriter
from .bunch import Bunch

import gym



"""
Some notes
==========
- Inherit from gym.Env. 
- Action space = ['check', 'fold', 'call', 'raise']
    - Can't just use spaces.Discrete for this because if you choose to raise, then we need another real valued number. 
    - Use spaces.Dict with Discrete for the action and 1d box for amount. 
- The Game class should be modified. 
    - 

"""







# setup a twiggy log
QUICK_SETUP()


## todo build a server and host the game, enabling human players to join
## todo build a small gui for playing the game
## todo Work out how to make a intellegant player.

class LessThan3PlayersError(Exception):
    pass


class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.do_checks()

    def __str__(self):
        return "{}{}".format(
            self.rank.upper() if isinstance(self.rank, str) else self.rank,
            self.suit.upper())

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
            raise ValueError('"rank" should be between A, K, Q, J or a number from 2 to 10. Got "{}"'.format(self.rank))

        if self.suit.lower() not in ['h', 'd', 's', 'c']:
            raise ValueError('"suit" should be one of h, d, s, c. Got "{}"'.format(self.suit))

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

    def __next__(self):
        return self.cards.__next()

    def __iter__(self):
        return self.cards.__iter__()

    def __str__(self):
        return f'{self.__class__.__name__}({self.cards})'

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

    def __getitem__(self, item):
        return self.cards.__getitem__(item)

    def __setitem__(self, key, value):
        return self.cards.__setitem__(key, value)

    def __delitem__(self, key):
        return self.cards.__delitem__(key)

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

    def place(self, position, card):
        d = Deck()
        deck = [i for i in self.cards if str(i) != str(card)]
        deck.insert(position, card)
        d.cards = deck
        return d


class Table:
    """
    #todo build a way of saving and loading a players information - stack, stats etc.

    """

    def __init__(self, players, game=None, stakes=(0.05, 0.10),
                 name='tumbleweed', script=None, reader=PokerStarsParser,
                 writer=PokerStarsWriter, **kwargs):
        self.name = name
        self.players = players
        self.stakes = stakes
        self.game = game
        self.script = script
        self.reader = reader
        self.writer = writer
        self.kwargs = kwargs

        if self.game is None:
            self.game = self.create_game()

        self.deck = Deck()

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
        # todo: in parsing a hand. make sure that if we know a players hand, that players hole cards are assigned
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

    def deal_flop(self, cards=None):
        if not isinstance(self.game, Game):
            raise ValueError(f'game argument should be of type "Game" '
                             f'but got "{type(self.game)}" instead.')

        if not isinstance(cards, list):
            raise ValueError

        if len(cards) != 3:
            raise ValueError
        if cards is not None:
            flop = cards
        else:
            flop = []
            for i in range(3):
                card = self.deck.pop()
                flop.append(card)
        self.game.game_info.community_cards += flop
        assert len(self.game.game_info.community_cards) < 6, "Got wrong number of communit cards: {}".format(
            self.game.game_info.community_cards)
        return self.game

    def deal_turn(self, card=None):
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

        winner = {k: v for k, v in hands.items() if v == max(list(hands.values()))}
        showdown = self.game.game_info.action_history['showdown']
        for pos, player in self.game.players.items():
            if player.status in ['folded', 'Empty', 'sitting-out']:
                continue
            showdown.append({
                'name': player.name,
                'position': player.position,
                'hand': hands[pos],
                'winner': True if list(winner.keys())[0] == pos else False
            })

        return self.game

    def play_game(self, to='river', flop=None, turn=None, river=None):

        # todo introduce a 'which' argument to only play single street. Mutual exclusive with 'to'. ensure we dont play out of correct order
        # todo enable replaying a game from a script
        # todo include a recorder argument which can be PokerStars, or another Vender. For writing to file
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
        for pos, pl in self.players.items():
            if pl.status == 'Empty':
                continue
            elif pl.stack == 0:
                LOG.critical('player {} went all in and has stack={}. Setting to sitting out'.format(pos, pl.stack))
                pl.status = 'sitting-out'
            elif pl.status == 'folded':
                pl.status = 'playing'

        num_playing = len({k: v for k, v in self.players.items() if v.status == 'playing'})
        if num_playing < 3:
            raise LessThan3PlayersError('Playing with less than 3 players is not yet supported')

        for street in streets:
            # rigged_cards = None
            # if street.__name__ == 'deal_flop' and flop is not None:
            #     rigged_cards = flop
            #
            # elif street.__name__ == 'deal_turn' and turn is not None:
            #     rigged_cards = turn
            #
            # elif street.__name__ == 'deal_river' and river is not None:
            #     rigged_cards = river

            self.game = street()
            LOG.debug(f'Street: {self.game.game_info.current_street}')
            ##reset the has_checked flag for current street
            self.game.game_info.check_available = False

            betting_dct = {k: 0 for k, v in self.game.players.items() if v.status
                           not in ['sitting-out', 'folded', 'Empty', 'all-in']}
            ## account for blinds
            if self.game.game_info.current_street == 'preflop':
                betting_dct['sb'] = self.game.game_info.stakes[0]
                betting_dct['bb'] = self.game.game_info.stakes[1]

            ## account for everybody folding to one player
            if len(self.get_those_still_playing()) == 1:
                LOG.warning('1 player left')
                winner = self.get_those_still_playing()
                win_pos = list(winner.keys())[0]
                LOG.debug(f'winner is {winner}')
                self.game.game_info['winner'] = {
                    'position': pos,
                    'name': winner[pos].name,
                    'hand': Hand(hole_cards=self.players[list(winner.keys())[0]].hole_cards,
                                 community_cards=self.game.game_info.community_cards)}
                ## pay winner
                self.players[self.game.game_info['winner']['position']].stack += self.game.game_info.pot
                break

            self._game_play(betting_dct)

            if self.game.game_info.current_street != 'river':
                self.game = self.next_street()

        if self.game.game_info.current_street == 'river' and to != 'turn':
            self.game = self.showdown()

            self.game.game_info['winner'] = self.get_winner(self.game)

            ## pay winner
            self.players[self.game.game_info['winner']['position']].stack += self.game.game_info.pot

        LOG.debug(f'winner of '
                  f'{self.game.game_info.pot} is: '
                  f'{self.game.game_info["winner"]["position"]} with '
                  f'{self.game.game_info["winner"]["hand"]}')
        LOG.debug(f'\tother players had:')
        for pl in self.game.game_info.action_history['showdown']:
            LOG.debug(f'\t\t{pl["position"]}, hand:{pl["hand"]}')
        return self.game

    def _game_play(self, betting_dct):
        LOG.warning(f'playing {self.game.game_info.current_street}')
        while len(list(set(betting_dct.values()))) != 1 or all(v == 0 for v in betting_dct.values()):
            ## get the position of the player who's turn it is
            curr_position = self.game.game_info.current_position
            player = self.game.players[curr_position]
            ## ignore empty, sitting out and folded players
            if player.status in ['Empty', 'sitting-out', 'folded', 'all-in']:
                self.game.game_info.current_position = self.next_position()
                continue

            ## get the action from the player
            action = self.request_action(player, betting_dct)

            if action['action'] not in ['check', 'fold']:
                self.game.game_info.check_available = False
                betting_dct[curr_position] += deepcopy(action['amount'])
            # update the action history with the players action
            street = self.game.game_info.current_street
            history = self.game.game_info.action_history[street]
            history.append(action)
            ## change to next position
            self.game.game_info.current_position = self.next_position()
            ## if player folds, remove him from betting dict
            if action['action'] == 'fold':
                del betting_dct[curr_position]
            LOG.debug(f'Current position={player.position}, action={action["action"]}, '
                      f'amount= {action["amount"]}')

    def get_those_still_playing(self):
        """
        get players that are still playing in this game
        Returns:
            list of players playing in the game
        """
        return {k: v for k, v in self.game.players.items() if v.status == 'playing'}

    def request_action(self, player, betting_dct):
        """
        I think there is a problem with ordering. We need a different or a copy
        of the pot for each round and player so that we can keep track of the evolution of
        the pot in hand history
        Returns:

        """
        bb = self.game.game_info.stakes[1]
        ## if the 'has_checked' flag is True, all players before have checked and we also have the option to check
        if self.game.game_info.check_available:
            action = player.process_turn(self.game.action_set_with_check, betting_dct, bb)
        else:
            ## if not, then we remove the option to check
            action = player.process_turn(self.game.action_set_without_check, betting_dct, bb)
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
            try:
                g = self.play_game()
                winning_hands.append(g.game_info.winner)
                self.reset_game()
            except LessThan3PlayersError:
                LOG.info('Game ended as less than 3 players are still playing')
                break

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


class RiggedTable(Table):

    def __init__(self, game, name='rigged', **kwargs):
        super().__init__(players=game.players, stakes=game.stakes,
                         # reader=game.reader, writer=game.writer,
                         **kwargs)
        print(self.deck, type(self.deck))
        cards = game.game_info.community_cards
        print('cards', cards)
        # cards = list(reversed(cards))
        # print('rev cards', cards)
        for i in range(len(cards)):
            if cards[i] in [False, None]:
                i -= 1
                continue
            print(i, cards[i], type(cards[i]), )
            r, s = list(cards[i])
            print(r, s)
            # try:
            c = Card(rank=int(r), suit=s)
            # except

            self.deck = self.deck.place(i, c)

        # where did the game get to?
        # print(game)
        # print(game.community_cards)


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

        self._btn = [v.name for k, v in self.players.items() if k == 'btn'][0]
        self._sb = [v.name for k, v in self.players.items() if k == 'sb'][0]
        self._bb = [v.name for k, v in self.players.items() if k == 'bb'][0]

        self.pot = 0
        self.seats = self._create_seats()
        self._validate_players()
        self.seats = self._fill_seats()
        self._set_game_info_defaults()

        for k, v in self.game_info.items():
            setattr(self, k, v)

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

    @staticmethod
    def from_parser(hand):
        #todo ensure hole cards are filled in parser
        #todo ensure players who are sitting out are sitting out.

        p = PokerStarsParser(hand)

        current_player = p.button()
        current_position = 'btn'
        pos_dct = {(current_player, current_position): p.player_info()[current_player]}
        while len(pos_dct) != 9:
            if current_player == 9:
                current_player = 1
            else:
                current_player += 1
            current_position = Position(current_position).next_position()
            try:
                pos_dct[(current_player, current_position)] = p.player_info()[current_player]
            except KeyError:
                pos_dct[(current_player, current_position)] = 'Empty'

        players = Players({})
        for k, v in pos_dct.items():
            player_num, pos = k
            if v == 'Empty':
                players[pos] = EmptySeat(position=pos)
            else:
                player_name, stack = v
                players[pos] = Player(name=player_name, stack=stack, position=pos)
            if player_name in p.sitting_out():
                players[pos].status = 'sitting-out'

        g = Game(players)
        g.game_info.datetime = p.datetime()
        g.game_info.game_id = p.game_id()
        g.game_info.stakes = p.steaks()
        g.game_info.community_cards = p.flop() + [p.turn()] + [p.river()]
        g.game_info.action_history['preflop'] = p.preflop_actions()
        g.game_info.action_history['flop'] = p.flop_actions()
        g.game_info.action_history['turn'] = p.turn_actions()
        g.game_info.action_history['river'] = p.river_actions()
        g.game_info.pot = p.winner()['cash']
        g.game_info.winner = p.winner()['player']
        lines = g.extract_lines()

        for pos, pl in g.players.items():
            if pl.status == 'Empty':
                continue
            g.players[pos] = Slave(pl.name, pl.stack,
                                   line=lines[pos], cards=pl.cards,
                                   status=pl.status, position=pos)

        return g

    def extract_lines(self):
        # position dict for looking up position and using as keys
        positions = self.positions()
        dct = {}
        for street, history in self.action_history.items():
            if isinstance(history, bool):
                continue
            for action in history:
                player = action['player']
                if player not in dct:
                    try:
                        dct[positions[player]] = []
                    except KeyError:
                        LOG.warning('player {} not found in positions '
                                    'dct. Bypassing this player with a continue. '.format(player))
                        continue
                dct[positions[player]].append(action)
        return dct

    def extract_lines_as_string(self):
        dct = {}
        for street, history in self.action_history.items():
            if isinstance(history, bool):
                continue

            try:
                dct[player] += street + ','
            except UnboundLocalError:
                pass

            for action in history:
                player = action['player']
                del action['player']
                if player not in dct:
                    dct[player] = ''
                dct[player] += action['action'] + ','
        return dct

    def positions(self):
        return {v.name: k for k, v in self.players.items()}


class Yaml:

    def __init__(self):
        pass

    def _yaml(self):
        yaml = ryaml()
        classes = [Game, Position, Players, Player, Card,
                   Bunch, EmptySeat, Hand, HighCard,
                   Pair, TwoPair, ThreeOfAKind,
                   Straight, Flush, FullHouse,
                   StraightFlush, RoyalFlush, datetime,
                   PokerStarsParser, PokerStarsParser.datetime
                   ]
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




class PokerGym(gym.Env):

    action_space = gym.spaces.Dict({
        'actions': gym.spaces.Discrete(4),
        'amount': gym.spaces.Box(0, 1e99, shape=(1,), dtype=np.float32)
    })

    # 0, 1, 2, 3 maps to check fold call and raise
    observation_space = gym.spaces.Dict({
        'street': gym.spaces.Discrete(5),
        'players': gym.spaces.Dict({
            'current': gym.spaces.Discrete(9),
            'identity': gym.spaces.Discrete(9)
        }),
        'community_cards': gym.spaces.MultiDiscrete([52]*5),
        'pot': gym.spaces.Box(0, 1e99, shape=(1,)),
        'history': gym.spaces.Dict({

        }),
        'stats': gym.spaces.Dict({

        })
    })
    deck = Deck().shuffle()

    def __init__(self, players):
        self.players = players

    def _step(self):
        """
        Simulates one complete hand of texas holdem poker
        Returns:

        """

    def _reset(self):
        pass

#
# 'currency': '$',
# 'datetime': datetime.now(),
# 'game_id': 1,
# 'check_available': True,  ## determines which action set a player is presented with
# 'betting_equal': False,  ## Criteria for ending a round of betting
# 'stakes': [0.10, 0.25],
# 'vendor': 'PokerStars',
# 'current_street': 'preflop',
# 'current_position': 'utg1',
# 'community_cards': [],
# 'pot': 0,
# 'call_amount': None,
# 'action_history': dict(
#     preflop=[],
#     flop=[],
#     turn=[],
#     river=[],
#     showdown=[],
# ),





