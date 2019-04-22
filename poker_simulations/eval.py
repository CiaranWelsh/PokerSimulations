from collections import OrderedDict, Counter, deque
from copy import deepcopy


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