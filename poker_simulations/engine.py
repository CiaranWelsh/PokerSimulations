import os, glob
from collections import OrderedDict, Counter, deque
from itertools import cycle
from random import shuffle
from copy import deepcopy
import logging, numpy

FORMAT = "%(name)s: %(levelname)s: %(funcName)s: %(message)s"
logging.basicConfig(format=FORMAT)
LOG = logging.getLogger(__name__)

POSITIONS = {
    1: 'btn',
    2: 'sb',
    3: 'bb',
    4: 'utg1',
    5: 'utg2',
    6: 'mp1',
    7: 'mp2',
    8: 'mp3',
    9: 'co',
}

POSITIONS_INVERTED = {v: k for k, v in POSITIONS.items()}


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


class Player:

    def __init__(self, name, cash, seat,
                 position, cards=[], currency='$'):
        self.name = name
        self.cash = round(cash, 2)
        self.seat = seat
        self.position = position
        self.cards = cards
        self.currency = currency

    def __str__(self):
        return f"Player(\"{self.name}\", cash={self.cash}{self.currency}, seat={self.seat}, position=\"{self.position}\")"

    def __repr__(self):
        return self.__str__()

    def bet(self, amount):
        self.cash -= amount
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


class Players:

    def __init__(self, iterable):
        self.num_players = len(iterable)

        if isinstance(iterable, list):
            iterable = {position: player for position, player in zip(
                list(POSITIONS.values())[:self.num_players], iterable)}

        if isinstance(iterable, dict):
            for k in iterable:
                if k not in POSITIONS.values():
                    raise ValueError(f'"{k}" is not a valid key for "Players".'
                                     f' These are valid: {POSITIONS.values()}')

        self.iterable = iterable

    def __str__(self):
        return self.iterable.__str__()

    def __getitem__(self, item):
        if item == 0:
            raise ValueError('cannot get item "0" as indexing starts at 1')
        if isinstance(item, int):
            item = POSITIONS[item]
        assert isinstance(item, str)
        return self.iterable[item]

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
        p = [Player(name='player{}'.format(i), cash=1.0,
                    seat=seats[i], position=POSITIONS[positions[i]]) for i in range(1, 9)]
        return p


class Seat:

    def __init__(self, position, player=None):
        self.position = position
        self.player = player

        if self.position not in POSITIONS.values():
            raise ValueError

    @property
    def isempty(self):
        if self.player is None:
            return True
        return False

    def __str__(self):
        return f'Seat(position="{self.position}", player={self.player})'

    def __repr__(self):
        return self.__str__()


class Table:

    def __init__(self, name, players, steaks=(0.05, 0.10)):
        self.name = name
        self.players = players
        self._game_id = 0
        self.steaks = steaks

        self.pot = 0

        ## initialise seats
        self.seats = {k: Seat(position=v) for k, v in POSITIONS.items()}
        for k, v in POSITIONS.items():
            setattr(self, v, self.seats[k])

    @property
    def game_id(self):
        return self._game_id

    @game_id.setter
    def game_id(self, id):
        if not isinstance(id, int):
            raise ValueError
        self._game_id = id

    # def add_player(self, player):
    #     if not isinstance(player, Player):
    #         raise ValueError(f"Expected a Plauer object. Got a {type(player)}")
    #     self.seats[player.seat].player = player
    #
    # def seat_players(self):
    #     if isinstance(self.players, Player):
    #         self.players = [self.players]
    #
    #     if isinstance(self.players, list):
    #         for i in self.players:
    #             if not isinstance(i, Player):
    #                 raise ValueError('Expected a Player object.')
    #
    #     for i in range(1, len(self.players) + 1):
    #         self.add_player(self.players[i - 1])

    def __str__(self):
        return f'Table(name="{self.name}")'

    # def play_game(self, game=None):
    #     self.game_id += 1
    #     g = Game(self.game_id, self.players)
    #     g.blinds()
        # g.deal()
        # g.preflop()
        # g.flop()
        # g.flop_bet()
        # g.turn()
        # g.turn_bet()
        # g.river()
        # g.river_bet()


class Game:

    def __init__(self, id, players, steaks=(0.05, 0.10)):
        self.id = id
        self.pot = 0

        if not isinstance(players, Players):
            players = Players(players)

        self.players = players
        self.steaks = steaks

        self.deck = Deck().shuffle()

    def positions(self):
        seats = OrderedDict()
        for p in self.players:
            seats[p] = self.players[p].name
        return seats

    def blinds(self):
        self.pot += self.players['sb'].bet(self.steaks[0])
        self.pot += self.players['bb'].bet(self.steaks[1])

    def deal(self):
        # hole cards
        for pos in POSITIONS.values():
            card = deepcopy(self.deck.pop())
            player = self.players[pos]
            player.cards.append(card)
            # print(pos, card)

        for pos in POSITIONS.values():
            card = self.deck.pop()
            self.players[pos].cards.append(card)

    @property
    def hole_cards(self):
        hole = OrderedDict()
        ## card 1
        for i in range(1, self.num + 1):
            hole[i] = [self.deck.pop()]

        ## card 2
        for i in range(1, self.num + 1):
            hole[i].append(self.deck.pop())
        return hole

    @property
    def flop(self):
        flop = []
        for i in range(3):
            flop.append(self.deck.pop())
        return flop

    @property
    def turn(self):
        return self.deck.pop()

    @property
    def river(self):
        return self.deck.pop()

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
