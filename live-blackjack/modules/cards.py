# LOGICA DELLE CARTE
# funzioni "pure": lavorano solo su liste e dizionari,
# non sanno nulla di Flask né del database
import random

SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']


def new_deck():
    deck = []
    for suit in SUITS:
        for rank in RANKS:
            deck.append({'rank': rank, 'suit': suit})
    random.shuffle(deck)
    return deck


def card_value(card):
    if card['rank'] in ['J', 'Q', 'K']:
        return 10
    if card['rank'] == 'A':
        return 11
    return int(card['rank'])


def hand_value(hand):
    total = 0
    aces = 0
    for card in hand:
        total += card_value(card)
        if card['rank'] == 'A':
            aces += 1

    # se sballa, gli assi valgono 1 invece di 11
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total


def dealer_turn(hand, deck):
    # il banco pesca finché non arriva almeno a 17
    while hand_value(hand) < 17:
        hand.append(deck.pop())


def winner(player_hand, dealer_hand):
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
