# ciclo di una mano: inizio, pesca, banco, risultato
# le carte sono gestite da modules/cards.py, la memoria è il database
from models.conn import db
from models.model import Player, Game
from modules import cards

# punti guadagnati o persi in base al risultato
SCORE_DELTA = {'win': 10, 'draw': 0, 'loss': -10}


# cerca la mano ancora in corso di un giocatore (se esiste)
def active_game(player_id):
    return db.session.scalars(
        db.select(Game).filter_by(player_id=player_id, status='playing')
    ).first()


# trasforma la mano in un dizionario pronto per il template
def game_data(hand):
    data = {
        'status': hand.status,
        'player_hand': hand.player_hand,
        'dealer_hand': hand.dealer_hand,
        'player_value': cards.hand_value(hand.player_hand),
        'dealer_value': cards.hand_value(hand.dealer_hand),
    }
    if hand.status == 'finished':
        data['outcome'] = hand.outcome
        data['delta'] = SCORE_DELTA[hand.outcome]
    return data


# inizia una nuova mano: distribuisce le carte e le salva nel database
def start_game(player):
    # elimina una eventuale mano rimasta a metà (per esempio dopo un refresh)
    old = active_game(player.id)
    if old:
        db.session.delete(old)

    deck = cards.new_deck()
    hand = Game(player_id=player.id)

    # il giocatore riceve 2 carte, il banco 1
    hand.player_hand = [deck.pop(), deck.pop()]
    hand.dealer_hand = [deck.pop()]
    hand.deck = deck

    db.session.add(hand)
    db.session.commit()

    # se il giocatore fa subito 21 la mano si chiude da sola
    if cards.hand_value(hand.player_hand) == 21:
        dealer_finishes(hand)


# il giocatore chiede una carta
def player_draws(hand):
    deck = list(hand.deck)
    cards_in_hand = list(hand.player_hand)
    cards_in_hand.append(deck.pop())
    hand.deck = deck
    hand.player_hand = cards_in_hand
    db.session.commit()

    value = cards.hand_value(cards_in_hand)

    # se sballa o fa 21 la mano finisce e tocca al banco
    if value >= 21:
        dealer_finishes(hand)


# il giocatore si ferma: gioca il banco e si chiude la mano
def player_stands(hand):
    dealer_finishes(hand)


# il banco completa la sua mano e poi si chiude la partita
def dealer_finishes(hand):
    deck = list(hand.deck)
    dealer_cards = list(hand.dealer_hand)
    cards.dealer_turn(dealer_cards, deck)
    hand.dealer_hand = dealer_cards
    hand.deck = deck
    finish_game(hand)


# chiude la mano: calcola il risultato e aggiorna il punteggio del giocatore
def finish_game(hand):
    hand.outcome = cards.winner(hand.player_hand, hand.dealer_hand)
    hand.status = 'finished'

    player = db.session.get(Player, hand.player_id)
    delta = SCORE_DELTA[hand.outcome]

    player.score += delta
    if hand.outcome == 'win':
        player.wins += 1
    elif hand.outcome == 'loss':
        player.losses += 1
    else:
        player.draws += 1

    db.session.commit()
