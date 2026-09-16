import random

SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']


def new_deck():
    deck = [{'rank': r, 'suit': s} for s in SUITS for r in RANKS]
    random.shuffle(deck)
    return deck


def card_value(card):
    if card['rank'] in ['J', 'Q', 'K']:
        return 10
    if card['rank'] == 'A':
        return 11
    return int(card['rank'])


def hand_value(hand):
    total = sum(card_value(c) for c in hand)
    aces = sum(1 for c in hand if c['rank'] == 'A')
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total


def dealer_play(hand, deck):
    # Il banco pesca fino ad arrivare almeno a 17
    while hand_value(hand) < 17:
        hand.append(deck.pop())
    return hand


def resolve_outcome(player_hand, dealer_hand):
    pv = hand_value(player_hand)
    dv = hand_value(dealer_hand)
    if pv > 21:
        return 'loss'
    if dv > 21:
        return 'win'
    if pv > dv:
        return 'win'
    if pv < dv:
        return 'loss'
    return 'draw'


SCORE_DELTA = {'win': 10, 'draw': 2, 'loss': -5}


def outcome_to_dict(player_hand, dealer_hand, outcome):
    return {
        'outcome': outcome,
        'delta': SCORE_DELTA[outcome],
        'player_value': hand_value(player_hand),
        'dealer_value': hand_value(dealer_hand),
    }
