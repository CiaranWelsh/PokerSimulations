import os, glob
from collections import OrderedDict, Counter, deque
from itertools import cycle
from random import shuffle
from copy import deepcopy
import logging, numpy
from .bunch import Bunch

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
        return f"stack({round(self.amount, 2)}{self.currency})"


class BasePlayer:

    def __init__(self, name, stack, seat,
                 position, cards=[], currency='$',
                 status='playing', bet=None):
        self.name = name
        if not isinstance(stack, Stack):
            stack = Stack(stack)

        self.stack = stack
        self.seat = seat
        self.position = position
        self.status = status
        self.bet = bet
        self.cards = deepcopy(cards)
        self.currency = currency

        if self.status not in ['playing', 'not-playing']:
            raise ValueError

    def __str__(self):
        return f"Player(name=\"{self.name}\", stack={self.stack}{self.currency}, seat={self.seat}, position=\"{self.position}\", status=\"{self.status}\")"

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
        if not isinstance(other, BasePlayer):
            raise TypeError('Cannot make comparison between Player and "{}"'.format(type(other)))

        return POSITIONS_INVERTED[self.position] > POSITIONS_INVERTED[other.position]

    def __lt__(self, other):
        if not isinstance(other, BasePlayer):
            raise TypeError('Cannot make comparison between Player and "{}"'.format(type(other)))

        return POSITIONS_INVERTED[self.position] < POSITIONS_INVERTED[other.position]

    def __ge__(self, other):
        if not isinstance(other, BasePlayer):
            raise TypeError('Cannot make comparison between Player and "{}"'.format(type(other)))
        return POSITIONS_INVERTED[self.position] >= POSITIONS_INVERTED[other.position]

    def __le__(self, other):
        if not isinstance(other, BasePlayer):
            raise TypeError('Cannot make comparison between Player and "{}"'.format(type(other)))
        return POSITIONS_INVERTED[self.position] <= POSITIONS_INVERTED[other.position]

    def __eq__(self, other):
        if not isinstance(other, BasePlayer):
            raise TypeError('Cannot make comparison between Player and "{}"'.format(type(other)))
        return POSITIONS_INVERTED[self.position] == POSITIONS_INVERTED[other.position]

    def __ne__(self, other):
        if not isinstance(other, BasePlayer):
            raise TypeError('Cannot make comparison between Player and "{}"'.format(type(other)))
        return POSITIONS_INVERTED[self.position] != POSITIONS_INVERTED[other.position]

    def check(self):
        return None

    def call(self, amount):
        if self.stack - amount < 0:
            LOG.info('Not enough money to call. Going all in.')
            self.all_in()
        self.stack -= amount

    def all_in(self):
        self.stack = 0

    def raise_(self, amount):
        if self.stack - amount < 0:
            LOG.info(f'Not enough money to raise by '
                     f'{amount}. Going all in.')
            self.all_in()
        self.stack -= amount

    def take_turn(self, available, probs=None):
        return numpy.random.choice(available, p=probs)

    def rotate_position(self):
        if self.position == 'btn':
            self.position = 'sb'
        elif self.position == 'sb':
            self.position = 'bb'
        elif self.position == 'bb':
            self.position = 'utg1'
        elif self.position == 'utg1':
            self.position = 'utg2'
        elif self.position == 'utg2':
            self.position = 'mp1'
        elif self.position == 'mp1':
            self.position = 'mp2'
        elif self.position == 'mp2':
            self.position = 'mp3'
        elif self.position == 'mp3':
            self.position = 'co'
        elif self.position == 'co':
            self.position == 'btn'


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

    def __getitem__(self, item):
        if isinstance(item, int):
            item = POSITIONS[item]
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
        p = [BasePlayer(name='player{}'.format(i), stack=1.0,
                        seat=seats[i], position=POSITIONS[positions[i]]) for i in range(1, 9)]
        return p


class Seat:

    def __init__(self, player=None):
        self._player = player

    @property
    def isempty(self):
        if self.player is None:
            return True
        return False

    @property
    def player(self):
        return self._player

    @player.setter
    def player(self, player):
        if not isinstance(player, BasePlayer):
            raise TypeError
        self._player = player

    def __str__(self):
        if self.isempty:
            return "Seat(player=\"Empty\")"
        else:
            return f"Seat(player=\"{self.player.name}\")"

    def __repr__(self):
        return self.__str__()


class SeatRank:
    ranks = ['btn', 'sb', 'bb',
             'utg1', 'utg2',
             'mp1', 'mp2', 'mp3',
             'co']

    numeric_ranks = [i for i in range(len(ranks))]

    def __init__(self, rank):
        self.rank = rank
        self.ranks = cycle(self.ranks)

        if rank not in self.ranks:
            raise ValueError

        ## iterate to current rank
        for r in self.ranks:
            if r == self.rank:
                break

    def __add__(self, other):
        assert isinstance(other, int)

        for i in range(other):
            new_rank = self.ranks.__next__()
        return SeatRank(new_rank)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.rank == other
        elif isinstance(other, SeatRank):
            return self.rank == other.rank

    def __ne__(self, other):

        if isinstance(other, str):
            return self.rank != other
        elif isinstance(other, SeatRank):
            return self.rank != other.rank

    def __str__(self):
        return self.rank


class Dealer:

    def __init__(self):
        self.deck = Deck()
        self.deck.shuffle()

    def deal(self, players):
        for i in [0, 1]:
            for pos in POSITIONS.keys():
                card = deepcopy(self.deck.pop())
                players[pos].cards.append(card)
        return players

    def flop(self, game):
        flop = []
        for i in range(3):
            flop.append(self.deck.pop())
        game.cards.flop = flop
        return game

    def turn(self, game):
        game.cards.turn = self.deck.pop()
        return game

    def river(self, game):
        game.cards.river = self.deck.pop()
        return game


class Table:

    def __init__(self, name, players, stakes=(0.05, 0.10)):
        self.name = name
        self.players = players
        self.stakes = stakes

        self.dealer = Dealer()

        self.pot = 0
        self._game_id = -1 #so that table starrts at 0

        ## initialise seats
        self.seats = {v: Seat() for k, v in POSITIONS.items()}
        self.seat_players()
        self.create_game()

    def register_player(self, player, seat):
        self.seats[seat] = player

    def play_game(self, game=None):
        if game is None:
            self.game_id += 1
            g = Game(self.game_id, self.players)

        else:
            g = game
        # g.restart()  ## for reseting the table and rotating positions
        g.blinds()
        print(self.dealer.deal(self.players))
        # g.deal()
        # g.action(street='preflop')
        # g.bet(which='preflop')
        # g.flop()
        # g.bet(which='flop')
        # g.turn()
        # g.bet(which='turn')
        # g.river()
        # g.bet(which='river')

    @property
    def game_id(self):
        return self._game_id

    @game_id.setter
    def game_id(self, id):
        if not isinstance(id, int):
            raise ValueError
        self._game_id = id

    def seat_players(self):
        if isinstance(self.players, BasePlayer):
            self.players = [self.players]

        if isinstance(self.players, list):
            for i in self.players:
                if not isinstance(i, BasePlayer):
                    raise ValueError('Expected a Player object.')

        for player in self.players:
            self.seats[player.position].player = player

    def num_players(self):
        return len([self.players])

    def __str__(self):
        return f'Table(name="{self.name}")'

    def get_gameplay_order(self):
        l = []
        for seat in self.seats:
            if not self.seats[seat].isempty:
                if self.seats[seat].player.status != 'not-playing':
                    l.append(seat)
        return l

    def create_game(self):
        return Game(self.game_id+1, self.players)

    def restart(self):
        pass
        # print(self.seats)

    def rotate(self):
        for player in self.players:
            player.rotate_position()

        for player in self.players:
            self.seats[player.position] = player

        return None


class Game:
    streets = ['preflop', 'flop', 'turn', 'river']

    def __init__(self, id, players, steaks=(0.05, 0.10)):
        self.id = id
        self.pot = 0
        self.street = 'preflop'

        if not isinstance(players, Players):
            players = Players(players)

        self.players = players
        self.stakes = steaks

        self.dealer = Dealer()
        self.action_history = ActionHistory()

    def positions(self):
        seats = OrderedDict()
        for p in self.players:
            seats[p] = self.players[p].name
        return seats

    def blinds(self):
        self.players['sb'].raise_(self.stakes[0])
        self.players['bb'].raise_(self.stakes[1])

    def action(self, street='preflop'):
        print('asdads')
        for i in self.players:
            print(i)

    # def bet(self, which='preflop'):
    #     if which not in ['preflop', 'flop', 'turn', 'river']:
    #         raise ValueError(f'The value of the "which" argument '
    #                          f'must be one of "preflop", '
    #                          f'"flop", "turn" or "river"')
    #
    #     for pos in BETTING_ORDER:
    #         play = None
    #         player = self.players[pos]
    #         while play not in (None, 'check', 'call', 'raise'):
    #             play = input("Check, call or raise? (1, 2, 3)\n")
    #         if play == 'check':
    #             return self.check(player)
    #         elif play == 'call':
    #             return self.call(player)
    #         elif play == 'raise':
    #             return self.raise_(player)
    #         else:
    #             raise ValueError

    def best_cards(self):
        """
        get the player with the best cards
        and the cards
        :return:
        """
        results = OrderedDict()
        for i in self.hole_cards:
            all7 = self.hole_cards[i] + self.flop + [self.river] + [self.turn]
            results[i] = Hand(all7).eval()

        winner_dct = {i: results[i] for i in results if results[i] == max(results.values())}
        return winner_dct, results


class BetManager:
    context_options1 = ['check', 'call', 'raise', 'fold']
    context_options2 = ['call', 'raise', 'fold']
    stages = ['blinds', 'preflop', 'flop', 'turn', 'river']

    def __init__(self, players, stage='blinds', time_limit=30):
        self.players = players
        self.time_limit = time_limit
        self.stage = stage

    def clear(self):
        """
        reset the BetManager to defaults for new round
        :return:
        """
        for player in self.players:
            player.bet = 0
            player.status = 'in'

    def decision(self):
        has_bet = False
        call_amount = None
        for pos in BETTING_ORDER:
            player = self.players[pos]
            if has_bet:
                play = input('Call, raise or fold? (c, f, number)')
            else:
                play = input('Check, call, raise or fold? (k, c, f, number)')

            player.take_turn(play)


class GameState(Bunch):

    def __init__(self, game_rules={}, players=[], cards=[], actions={}):
        self.game_rules = game_rules
        self.players = players
        self.cards = cards
        self.actions = actions

        self.pot = 0

    def _set_defaults(self):
        for k, v in self._default_game_rules().item():
            if k not in self.game_rules:
                self.game_rules[k] = v

    def _default_game_rules(self):
        return {
            'num_players': 9,
        }

    def validate_players(self):
        pass


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
